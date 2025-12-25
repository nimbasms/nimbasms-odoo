# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

try:
    from nimbasms import Client, NimbaSMSException
except ImportError:
    Client = None
    NimbaSMSException = Exception


class SmsAfricanAccountWizard(models.TransientModel):
    """
    Wizard for configuring Nimba SMS Provider account.
    Opens as a modal when user clicks "Manage Account" in Settings.
    """
    _name = 'sms.nimba.account.wizard'
    _description = 'Nimba SMS Account Configuration Wizard'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    # Configuration fields
    nimba_service_id = fields.Char(
        string='Service ID',
        required=True,
        help='Your Service ID from the Nimba SMS dashboard'
    )
    nimba_secret_token = fields.Char(
        string='Secret Token',
        required=True,
        help='Your Secret Token from the Nimba SMS dashboard'
    )
    nimba_sender_name = fields.Char(
        string='Sender Name',
        required=True,
        help='Your approved sender name or short code'
    )

    @api.model
    def default_get(self, fields_list):
        """Load current company configuration when opening wizard."""
        res = super().default_get(fields_list)

        company = self.env.company
        res.update({
            'company_id': company.id,
            'nimba_service_id': company.sms_nimba_service_id or '',
            'nimba_secret_token': company.sms_nimba_secret_token or '',
            'nimba_sender_name': company.sms_nimba_sender_name or '',
        })

        return res

    def action_save(self):
        """
        Save configuration to res.company and close the wizard.

        :return: action to close the wizard modal
        """
        self.ensure_one()

        # Validate required fields
        if not self.nimba_service_id:
            raise UserError(_('Service ID is required'))
        if not self.nimba_secret_token:
            raise UserError(_('Secret Token is required'))
        if not self.nimba_sender_name:
            raise UserError(_('Sender Name is required'))

        # Save to company
        self.company_id.write({
            'sms_nimba_service_id': self.nimba_service_id,
            'sms_nimba_secret_token': self.nimba_secret_token,
            'sms_nimba_sender_name': self.nimba_sender_name,
        })

        # Close the wizard
        return {'type': 'ir.actions.act_window_close'}

    def action_test_connection(self):
        """
        Test connection to Nimba SMS provider using official SDK.

        This method validates the API credentials by checking account info.

        :return: notification action with success/failure message
        """
        self.ensure_one()

        # Check if SDK is available
        if Client is None:
            raise UserError(_('Nimba SMS SDK not installed. Please run: pip install nimbasms'))

        # Validate required fields first
        if not self.nimba_service_id:
            raise UserError(_('Please enter a Service ID before testing'))
        if not self.nimba_secret_token:
            raise UserError(_('Please enter a Secret Token before testing'))

        try:
            # Initialize client with credentials
            client = Client(self.nimba_service_id, self.nimba_secret_token)

            # Test connection by fetching account info
            response = client.accounts.get()

            if response.ok:
                # Success!
                balance = response.data.get('balance', 'N/A')
                message = _('Connection successful! Your credentials are valid.')
                if balance != 'N/A':
                    message += _('\nAccount Balance: %s') % balance

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success!'),
                        'message': message,
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                # Failed response
                error_msg = _('Authentication failed.')
                try:
                    error_data = response.data
                    if isinstance(error_data, dict):
                        error_msg = error_data.get('message', error_msg)
                except Exception:
                    pass

                raise UserError(error_msg)

        except NimbaSMSException as e:
            raise UserError(_('Nimba SMS Error: %s') % str(e))
        except Exception as e:
            raise UserError(_('Unexpected error: %s') % str(e))

    def action_cancel(self):
        """Close the wizard without saving."""
        return {'type': 'ir.actions.act_window_close'}
