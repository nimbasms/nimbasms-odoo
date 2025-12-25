# -*- coding: utf-8 -*-

from odoo import fields, models


class SmsSms(models.Model):
    _inherit = 'sms.sms'

    sms_nimba_sid = fields.Char(
        string='Nimba SMS ID',
        help='Message ID from Nimba SMS provider',
        readonly=True,
        copy=False,
    )

    def _split_by_api(self):
        """
        Override to handle Nimba SMS provider routing.

        This method routes SMS to the appropriate API
        based on the company's sms_provider setting.
        """
        from collections import defaultdict

        sms_by_company = defaultdict(lambda: self.env['sms.sms'])
        todo_via_super = self.browse()

        for sms in self:
            sms_by_company[sms._get_sms_company()] += sms

        for company, company_sms in sms_by_company.items():
            if company.sms_provider == "nimba":
                sms_api = company._get_sms_api_class()(self.env)
                sms_api._set_company(company)
                yield sms_api, company_sms
            else:
                todo_via_super += company_sms

        if todo_via_super:
            yield from super(SmsSms, todo_via_super)._split_by_api()

    failure_type = fields.Selection(
        selection_add=[
            ('nimba_auth_error', 'Nimba SMS: Authentication Error'),
            ('nimba_invalid_sender', 'Nimba SMS: Invalid Sender Name'),
            ('nimba_insufficient_balance', 'Nimba SMS: Insufficient Balance'),
        ],
        ondelete={
            'nimba_auth_error': 'cascade',
            'nimba_invalid_sender': 'cascade',
            'nimba_insufficient_balance': 'cascade',
        }
    )

    def _handle_call_result_hook(self, results):
        """
        Store the Nimba SMS provider message ID on both SMS and tracker.

        :param results: list of dicts in the form [{
            'uuid': Odoo's id of the SMS,
            'state': State of the SMS in Odoo,
            'sms_nimba_sid': Nimba SMS's id of the message,
        }, ...]
        """
        nimba_sms = self.filtered(
            lambda s: s._get_sms_company().sms_provider == 'nimba'
        )
        grouped_nimba_sms = nimba_sms.grouped("uuid")

        for result in results:
            sms = grouped_nimba_sms.get(result.get('uuid'))
            nimba_sid = result.get('sms_nimba_sid')

            if sms and nimba_sid:
                # Store on SMS record
                sms.write({'sms_nimba_sid': nimba_sid})

                # Also store on tracker if it exists
                if sms.sms_tracker_id:
                    sms.sms_tracker_id.sms_nimba_sid = nimba_sid

        # Call super for other SMS
        super(SmsSms, self - nimba_sms)._handle_call_result_hook(results)
