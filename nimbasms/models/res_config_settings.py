# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    """
    Extension of settings to add Nimba SMS provider configuration.
    These settings sync with res.company fields.
    """
    _inherit = 'res.config.settings'

    # SMS Provider selection
    sms_provider = fields.Selection(
        related='company_id.sms_provider',
        readonly=False,
        string='SMS Provider'
    )

    # Related fields from res.company
    sms_nimba_service_id = fields.Char(
        related='company_id.sms_nimba_service_id',
        readonly=False,
        string='Service ID'
    )
    sms_nimba_secret_token = fields.Char(
        related='company_id.sms_nimba_secret_token',
        readonly=False,
        string='Secret Token'
    )
    sms_nimba_sender_name = fields.Char(
        related='company_id.sms_nimba_sender_name',
        readonly=False,
        string='Sender Name'
    )


    def action_open_nimba_sms_manage(self):
        """
        Proxy method to open the Nimba SMS configuration wizard.
        Delegates to the company's method.
        """
        self.ensure_one()
        return self.company_id._action_open_nimba_sms_manage()
