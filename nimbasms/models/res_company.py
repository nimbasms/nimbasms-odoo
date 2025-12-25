# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.addons.nimbasms.tools.sms_api import SmsApiNimba


class ResCompany(models.Model):
    _inherit = 'res.company'

    # Define SMS provider selection including Nimba SMS
    # Includes all standard options (IAP, Twilio, Nimba)
    sms_provider = fields.Selection(
        string='SMS Provider',
        selection=[
            ('iap', 'Send via Odoo'),
            ('twilio', 'Send via Twilio'),
            ('nimba', 'Nimba SMS'),
        ],
        default='iap',
    )

    # Nimba SMS configuration fields
    sms_nimba_service_id = fields.Char(
        string='Nimba SMS Service ID',
        groups='base.group_system',
        help='Service ID from your Nimba SMS dashboard'
    )
    sms_nimba_secret_token = fields.Char(
        string='Nimba SMS Secret Token',
        groups='base.group_system',
        help='Secret Token from your Nimba SMS dashboard'
    )
    sms_nimba_sender_name = fields.Char(
        string='Nimba SMS Sender Name',
        groups='base.group_system',
        help='Your approved sender name or short code'
    )

    def _get_sms_api_class(self):
        """Return the SMS API class based on provider."""
        self.ensure_one()
        if self.sms_provider == 'nimba':
            return SmsApiNimba
        return super()._get_sms_api_class()

    def _action_open_nimba_sms_manage(self):
        """
        Open the Nimba SMS configuration wizard in a modal.

        This action is triggered when user clicks "Manage Account" button
        in the Settings page.

        :return: action dict that opens the wizard in a modal dialog
        """
        self.ensure_one()

        # Create wizard record with current configuration
        wizard = self.env['sms.nimba.account.wizard'].create({
            'company_id': self.id,
            'nimba_service_id': self.sms_nimba_service_id or '',
            'nimba_secret_token': self.sms_nimba_secret_token or '',
            'nimba_sender_name': self.sms_nimba_sender_name or '',
        })

        # Return action to open wizard in modal
        return {
            'type': 'ir.actions.act_window',
            'name': _('Configure Nimba SMS Account'),
            'res_model': 'sms.nimba.account.wizard',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',  # Opens in modal dialog
            'context': dict(self.env.context),
        }
