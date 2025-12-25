# -*- coding: utf-8 -*-
{
    'name': 'Nimba SMS',
    'version': '19.0.2.1.0',
    'category': 'Discuss/SMS',
    'summary': 'Integration with Nimba SMS using official Python SDK',
    'sequence': 100,  # Load after other SMS modules
    'description': """
        Nimba SMS Provider Integration (Official SDK)
        ==============================================

        This module integrates Nimba SMS (https://www.nimbasms.com/)
        into Odoo's SMS infrastructure using the official Python SDK.
        API documentation: https://developers.nimbasms.com

        Features:
        ---------
        * Send SMS through official Nimba SMS SDK
        * Batch sending - multiple recipients in one request
        * Webhook support for delivery status callbacks
        * Multi-tenant support with per-database configuration
        * Phone number validation for African countries (default: Guinea)
        * Account balance checking

        Configuration:
        --------------
        1. Install SDK: pip install nimbasms
        2. Configure credentials in Settings > General Settings > SMS section
        3. Use "Manage Account" button to enter Service ID and Secret Token
        4. Test connection to verify setup

        Requirements:
        -------------
        * nimbasms - Official Nimba SMS Python SDK
        * phonenumbers - Phone number validation
    """,
    'author': 'Nimba SMS Integration',
    'website': 'https://github.com/nimbasms/odoo-integration',
    'license': 'LGPL-3',
    'support': 'support@nimbasms.com',  # Optional: support email
    'depends': [
        'sms',
    ],
    'external_dependencies': {
        'python': [
            'nimbasms',
            'phonenumbers',
        ],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/nimba_sms_account_wizard_view.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
