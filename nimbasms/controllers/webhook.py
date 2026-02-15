# -*- coding: utf-8 -*-

import json
import logging
import hmac
import hashlib

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


# Nimba SMS status mapping to Odoo SMS states
NIMBA_TO_SMS_STATE = {
    'received': 'sent',   # Message successfully delivered to recipient
    'failed': 'error',    # Message delivery failed
}


class NimbaSmsWebhook(http.Controller):
    """
    Webhook controller for receiving delivery status callbacks from Nimba SMS provider.

    This controller handles incoming HTTP requests from the SMS provider
    to update the delivery status of sent messages.
    """

    @staticmethod
    def _normalize_phone(number):
        """Strip '+' prefix and spaces from a phone number for comparison."""
        if not number:
            return ''
        return number.lstrip('+').replace(' ', '').replace('-', '')

    @staticmethod
    def _find_sms_by_nimba_callback(sms_model, messageid, contact):
        """
        Find the specific sms.sms record matching a Nimba callback.

        NimbaSMS returns a single messageid for an entire batch of recipients.
        We use the contact phone number to identify the correct record.

        :param sms_model: sms.sms model (sudo'd)
        :param messageid: Nimba message ID
        :param contact: recipient phone number from the webhook
        :return: single sms.sms recordset (may be empty)
        """
        all_sms = sms_model.search([('sms_nimba_sid', '=', messageid)])
        if not all_sms:
            return sms_model  # empty recordset

        contact_normalized = NimbaSmsWebhook._normalize_phone(contact)
        if contact_normalized:
            target = all_sms.filtered(
                lambda s: NimbaSmsWebhook._normalize_phone(s.number) == contact_normalized
            )[:1]
            if target:
                return target

        # Fallback: return the first undelivered SMS, or just the first one
        pending = all_sms.filtered(lambda s: s.state not in ('sent', 'error'))[:1]
        return pending or all_sms[:1]

    @staticmethod
    def _update_sms_from_nimba_status(sms_record, status, error_message=None):
        """
        Update an sms.sms record based on Nimba webhook status.

        :param sms_record: sms.sms recordset (single record)
        :param status: Nimba status string ('received' or 'failed')
        :param error_message: optional error message for failed status
        """
        odoo_state = NIMBA_TO_SMS_STATE.get(status, 'error')
        update_vals = {'state': odoo_state}
        if odoo_state == 'error':
            update_vals['failure_type'] = 'sms_delivery'
        sms_record.write(update_vals)

    @http.route(['/sms/webhook/nimba', '/sms/webhook/nimba/<string:db_name>'], type='http', auth='public', methods=['POST', 'GET'], csrf=False)
    def nimba_sms_delivery_callback(self, db_name=None, **kwargs):
        """
        Handle delivery status callback from Nimba SMS.

        This endpoint receives POST requests from Nimba SMS when the
        delivery status of an SMS changes (received, failed, etc.).

        Expected payload format:
        {
            "messageid": "uuid-message-id",
            "contact": "+224627758293",
            "status": "received|failed",
            "error": "Error message if failed",
            "metadata": {"message_type": "API"}
        }

        :return: HTTP response with status 200
        """
        try:
            # Handle GET requests (webhook validation from providers)
            if request.httprequest.method == 'GET':
                _logger.info(f"Webhook validation GET request received for db={db_name}")
                return request.make_response(
                    json.dumps({'status': 'ok', 'message': 'Webhook endpoint is ready'}),
                    headers={'Content-Type': 'application/json'},
                    status=200
                )

            # Log the incoming webhook
            _logger.info(f"Received SMS webhook callback for db={db_name}: {kwargs}")

            # Get request data
            data = kwargs

            # If request is JSON, try to parse it
            if request.httprequest.content_type == 'application/json':
                try:
                    data = json.loads(request.httprequest.data.decode('utf-8'))
                except Exception as e:
                    _logger.error(f"Error parsing JSON webhook: {str(e)}")

            # For multi-tenant: if no db_name specified, try to find SMS in all databases
            if not db_name:
                # Try to process in all available databases
                return self._process_delivery_status_multi_tenant(data)

            # Validate webhook signature if configured (recommended for security)
            if not self._validate_webhook_signature(request):
                _logger.warning("Invalid webhook signature - rejecting request")
                return request.make_response(
                    json.dumps({'status': 'error', 'message': 'Invalid signature'}),
                    headers={'Content-Type': 'application/json'},
                    status=401
                )

            # Process the delivery status for specific database
            self._process_delivery_status(data)

            # Return success response
            return request.make_response(
                json.dumps({'status': 'success', 'message': 'Webhook processed'}),
                headers={'Content-Type': 'application/json'},
                status=200
            )

        except Exception as e:
            _logger.error(f"Error processing SMS webhook: {str(e)}", exc_info=True)
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers={'Content-Type': 'application/json'},
                status=500
            )

    def _process_delivery_status_multi_tenant(self, data):
        """
        Process delivery status across all databases (multi-tenant support).

        This is used when webhook is called without specifying a database name,
        which is the case with ngrok or when using a single webhook URL for all tenants.

        :param data: webhook payload data
        :return: HTTP response
        """
        import odoo
        from odoo.modules.registry import Registry

        messageid = data.get('messageid')
        if not messageid:
            _logger.warning(f"Nimba webhook missing messageid: {data}")
            return request.make_response(
                json.dumps({'status': 'error', 'message': 'Missing messageid'}),
                headers={'Content-Type': 'application/json'},
                status=400
            )

        contact = data.get('contact', '')
        status = data.get('status', '').lower()

        # Get list of all databases
        db_list = odoo.service.db.list_dbs(True)

        found = False
        for db_name in db_list:
            try:
                db_registry = Registry(db_name)
                with db_registry.cursor() as cr:
                    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})

                    # Find the specific SMS by messageid + contact number
                    SmsSms = env['sms.sms'].sudo()
                    sms = self._find_sms_by_nimba_callback(SmsSms, messageid, contact)

                    if not sms:
                        continue

                    # Try to update via tracker if available (linked via uuid)
                    SmsTracker = env['sms.tracker'].sudo()
                    tracker = SmsTracker.search([
                        ('sms_uuid', '=', sms.uuid),
                    ], limit=1) if sms.uuid else SmsTracker

                    if tracker:
                        if status == 'failed':
                            error_message = data.get('error', 'Delivery failed')
                            tracker._action_update_from_nimba_error(error_message)
                        elif status in NIMBA_TO_SMS_STATE:
                            odoo_state = NIMBA_TO_SMS_STATE[status]
                            tracker._action_update_from_sms_state(odoo_state)
                        cr.commit()
                        _logger.info(f"Updated SMS tracker {tracker.id} for sms.sms {sms.id} in '{db_name}' (messageid: {messageid}) to {NIMBA_TO_SMS_STATE.get(status, 'error')} for contact {contact}")
                    else:
                        # No tracker, update sms.sms directly
                        self._update_sms_from_nimba_status(sms, status)
                        cr.commit()
                        _logger.info(f"Updated SMS {sms.id} in '{db_name}' (messageid: {messageid}) to {NIMBA_TO_SMS_STATE.get(status, 'error')} for contact {contact}")

                    found = True
                    break

            except Exception as e:
                _logger.warning(f"Error processing webhook in database '{db_name}': {str(e)}")
                continue

        if not found:
            _logger.warning(f"Could not find SMS with sms_nimba_sid={messageid} in any database")
            return request.make_response(
                json.dumps({'status': 'warning', 'message': 'SMS not found in any database'}),
                headers={'Content-Type': 'application/json'},
                status=200  # Still return 200 to avoid retries
            )

        return request.make_response(
            json.dumps({'status': 'success', 'message': 'Webhook processed'}),
            headers={'Content-Type': 'application/json'},
            status=200
        )

    def _validate_webhook_signature(self, request):
        """
        Validate webhook signature for security.

        Some providers send a signature header to verify the webhook authenticity.
        Customize this method based on your provider's authentication method.

        :param request: HTTP request object
        :return: True if signature is valid or not configured, False otherwise
        """
        # Get webhook secret from configuration
        ICP = request.env['ir.config_parameter'].sudo()
        webhook_secret = ICP.get_param('sms.nimba_webhook_secret', default='')

        # If no secret configured, skip validation (SECURITY RISK!)
        if not webhook_secret:
            _logger.error(
                "SECURITY WARNING: Webhook secret not configured! "
                "Configure 'sms.nimba_webhook_secret' in System Parameters for production. "
                "Anyone can send fake webhooks and modify SMS statuses."
            )
            return True  # Accept anyway but log security warning

        # Get signature from headers (customize based on provider)
        signature_header = request.httprequest.headers.get('X-SMS-Signature', '')

        if not signature_header:
            return False

        # Compute expected signature
        payload = request.httprequest.data
        expected_signature = hmac.new(
            webhook_secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()

        # Compare signatures
        return hmac.compare_digest(signature_header, expected_signature)

    def _process_delivery_status(self, data):
        """
        Process the delivery status update from Nimba SMS webhook.

        Expected payload format:
        {
            "messageid": "7856a94c-5310-4d4c-bd73-fa4870ecd6c6",
            "status": "received",  // ou "failed"
            "contact": "+224623000000",
            "metadata": {"message_type": "API"}
        }

        :param data: webhook payload data
        """
        messageid = data.get('messageid')
        contact = data.get('contact', '')
        status = data.get('status', '').lower()

        if not messageid:
            _logger.warning(f"Nimba webhook missing messageid: {data}")
            return

        # Find the specific SMS by messageid + contact number
        SmsSms = request.env['sms.sms'].sudo()
        sms = self._find_sms_by_nimba_callback(SmsSms, messageid, contact)

        if sms:
            self._update_sms_from_nimba_status(sms, status)
            _logger.info(f"Updated SMS {sms.id} (messageid: {messageid}) to {NIMBA_TO_SMS_STATE.get(status, 'error')} for contact {contact}")
        else:
            _logger.warning(f"Could not find SMS with sms_nimba_sid={messageid} for contact {contact}")

    def _map_status_to_odoo(self, provider_status):
        """
        Map Nimba SMS status to Odoo SMS state.

        Nimba SMS webhook statuses (official documentation):
        - received: Message successfully delivered to recipient
        - failed: Message delivery failed

        Odoo states:
        - sent: Successfully delivered
        - error: Failed to deliver

        :param provider_status: status from Nimba SMS webhook
        :return: Odoo state
        """
        status_mapping = {
            'received': 'sent',   # Successfully delivered
            'failed': 'error',    # Delivery failed
        }

        return status_mapping.get(provider_status.lower(), 'error')

    @http.route('/sms/webhook/test', type='http', auth='user', methods=['GET'])
    def test_webhook_endpoint(self):
        """
        Test endpoint to verify webhook is accessible.

        This can be used to test if the webhook URL is properly configured
        in your infrastructure (Traefik, etc.).

        :return: JSON response confirming webhook is active
        """
        return request.make_response(
            json.dumps({
                'status': 'active',
                'message': 'Nimba SMS webhook is active',
                'endpoint': '/sms/webhook/nimba'
            }),
            headers={'Content-Type': 'application/json'},
            status=200
        )
