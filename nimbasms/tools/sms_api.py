# -*- coding: utf-8 -*-

import logging
import phonenumbers
from phonenumbers import NumberParseException

from odoo import _
from odoo.addons.sms.tools.sms_api import SmsApiBase

try:
    from nimbasms import Client, NimbaSMSException
except ImportError:
    _logger = logging.getLogger(__name__)
    _logger.warning("nimbasms library not found. Please install it: pip install nimbasms")
    Client = None
    NimbaSMSException = Exception

_logger = logging.getLogger(__name__)


class SmsApiNimba(SmsApiBase):
    """
    SMS API implementation for Nimba SMS providers.

    This class handles sending SMS through African providers like
    AfricasTalking, Hubtel, etc.
    """

    PROVIDER_TO_SMS_FAILURE_TYPE = SmsApiBase.PROVIDER_TO_SMS_FAILURE_TYPE | {
        'african_auth_error': 'sms_credit',
        'african_invalid_sender': 'sms_number_format',
        'african_insufficient_balance': 'sms_credit',
    }

    def _format_phone_number(self, number, default_country='GN'):
        """
        Format phone number to E.164 international format without '+' prefix.

        Nimba SMS SDK expects numbers in international format without the '+' sign.
        Example: '224620000000' for Guinea, not '+224620000000'
        """
        try:
            parsed = phonenumbers.parse(number, default_country)
            if not phonenumbers.is_valid_number(parsed):
                _logger.warning(f"Invalid phone number: {number}")
                return number
            # Format to E.164 and remove the '+' prefix
            formatted = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            return formatted.lstrip('+')
        except NumberParseException as e:
            _logger.warning(f"Error parsing phone number {number}: {str(e)}")
            return number

    def _send_sms_batch(self, messages, delivery_reports_url=False):
        """
        Send a batch of SMS using Nimba SMS official SDK.

        :param messages: list of message dicts with 'content' and 'numbers'
        :param delivery_reports_url: callback URL for delivery reports
        :return: list of result dicts with state and uuid
        """
        # Check if SDK is available
        if Client is None:
            _logger.error("Nimba SMS SDK not installed. Please run: pip install nimbasms")
            return [{
                'uuid': num_info['uuid'],
                'state': 'server_error',
                'failure_reason': _("Nimba SMS SDK not installed"),
            } for msg in messages for num_info in msg.get('numbers', [])]

        # Get company configuration
        company_sudo = (self.company or self.env.company).sudo()

        service_id = company_sudo.sms_nimba_service_id
        secret_token = company_sudo.sms_nimba_secret_token
        sender_name = company_sudo.sms_nimba_sender_name

        if not service_id or not secret_token or not sender_name:
            _logger.error("Nimba SMS Provider not configured properly")
            return [{
                'uuid': num_info['uuid'],
                'state': 'server_error',
                'failure_reason': _("Provider not configured: missing Service ID, Secret Token, or Sender Name"),
            } for msg in messages for num_info in msg.get('numbers', [])]

        # Initialize Nimba SMS client
        try:
            client = Client(service_id, secret_token)
        except NimbaSMSException as e:
            _logger.error(f"Failed to initialize Nimba SMS client: {e}")
            return [{
                'uuid': num_info['uuid'],
                'state': 'server_error',
                'failure_reason': _("Failed to initialize Nimba SMS client: %s") % str(e),
            } for msg in messages for num_info in msg.get('numbers', [])]

        res = []

        # Process each message
        for message in messages:
            body = message.get('content') or ''
            numbers_info = message.get('numbers') or []

            # Prepare list of formatted phone numbers and UUID mapping
            phone_numbers = []
            uuid_map = {}  # Map phone_number -> uuid

            for num_info in numbers_info:
                formatted_num = self._format_phone_number(num_info['number'])
                phone_numbers.append(formatted_num)
                uuid_map[formatted_num] = num_info['uuid']

            if not phone_numbers:
                continue

            try:
                # Send SMS batch via SDK
                # Nimba SMS SDK supports sending to multiple recipients in one request
                response = client.messages.create(
                    to=phone_numbers,
                    sender_name=sender_name,
                    message=body
                )

                if response.ok:
                    # Success: all messages sent
                    response_data = response.data

                    _logger.info(f"Nimba SMS batch sent successfully: {response_data}")

                    # Extract messageid from Nimba response for webhook tracking
                    # Response format: {"messageid": "uuid", "url": "..."}
                    nimba_messageid = response_data.get('messageid')

                    # Mark all as success (will be mapped to 'pending' state by Odoo)
                    # The webhook will then update to 'sent' when actually delivered
                    # NOTE: If Nimba API returns individual status per number,
                    # this logic should be updated to parse that
                    for phone in phone_numbers:
                        uuid = uuid_map[phone]
                        res.append({
                            'uuid': uuid,
                            'state': 'success',  # Mapped to 'pending' by Odoo core
                            'sms_nimba_sid': nimba_messageid,  # Store messageid for webhook matching
                            'failure_reason': False,
                            'failure_type': False,
                        })
                else:
                    # Global error: all messages failed
                    error_msg = _("Unknown error")
                    try:
                        error_data = response.data
                        error_msg = error_data.get('message', response.text)
                    except Exception:
                        error_msg = response.text or _("No error details available")

                    _logger.error(f"Nimba SMS error (status {response.status_code}): {error_msg}")

                    for phone in phone_numbers:
                        uuid = uuid_map[phone]
                        res.append({
                            'uuid': uuid,
                            'state': 'server_error',
                            'failure_type': 'server_error',
                            'failure_reason': error_msg,
                        })

            except NimbaSMSException as e:
                _logger.error(f"Nimba SMS SDK exception: {e}")
                for phone in phone_numbers:
                    uuid = uuid_map[phone]
                    res.append({
                        'uuid': uuid,
                        'state': 'server_error',
                        'failure_type': 'server_error',
                        'failure_reason': str(e),
                    })
            except Exception as e:
                _logger.error(f"Unexpected error sending SMS batch: {str(e)}", exc_info=True)
                for phone in phone_numbers:
                    uuid = uuid_map[phone]
                    res.append({
                        'uuid': uuid,
                        'state': 'server_error',
                        'failure_type': 'server_error',
                        'failure_reason': str(e),
                    })

        return res

    def _get_sms_api_error_messages(self):
        """Return error messages for different failure types."""
        error_dict = super()._get_sms_api_error_messages()
        error_dict.update({
            'african_auth_error': _("Authentication error - check API credentials"),
            'african_invalid_sender': _("Invalid sender name - verify it's approved"),
            'african_insufficient_balance': _("Insufficient balance in your account"),
            'wrong_number_format': _("Invalid phone number format"),
            'server_error': _("Server error - please try again"),
            'unknown': _("Unknown error - contact support"),
        })
        return error_dict
