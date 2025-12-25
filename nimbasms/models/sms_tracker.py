# -*- coding: utf-8 -*-

from odoo import models, fields


class SmsTracker(models.Model):
    _inherit = 'sms.tracker'

    sms_nimba_sid = fields.Char(string='Nimba SMS Message ID', readonly=True, help='Message ID from Nimba SMS provider')

    def _action_update_from_nimba_error(self, error_message):
        """
        Update the SMS tracker with Nimba SMS error information.

        :param error_message: Error message from Nimba SMS
        :return: Updated tracker
        """
        return self.with_context(
            sms_known_failure_reason=error_message
        )._action_update_from_provider_error('not_delivered')
