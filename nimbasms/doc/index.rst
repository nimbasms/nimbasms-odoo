Nimba SMS Provider for Odoo
============================

This module integrates Nimba SMS (https://www.nimbasms.com/) into Odoo's SMS infrastructure using the official Python SDK.

Data Privacy
------------

When using this module, SMS messages, recipient phone numbers, and delivery status information are sent to Nimba SMS service for processing and delivery. This is necessary for the module to function. Please review the `Nimba SMS Privacy Policy <https://www.nimbasms.com/conditions-generales-d-utilisation>`_ for information on how your data is handled.

Features
--------

* Send SMS through official Nimba SMS SDK
* Batch sending - multiple recipients in one request
* Webhook support for delivery status callbacks
* Multi-tenant support with per-database configuration
* Phone number validation for African countries (default: Guinea)
* Account balance checking

Installation
------------

1. Install Python dependencies:

   .. code-block:: bash

      pip install nimbasms phonenumbers

2. Place the module in your Odoo addons directory

3. Restart Odoo server

4. Go to **Apps** menu, click **Update Apps List**, search for "Nimba SMS" and click **Install**

Configuration
-------------

Step 1: Get Your Nimba SMS Credentials
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Sign up at https://www.nimbasms.com
2. Log in to your Nimba SMS dashboard
3. Navigate to **Dashboard → Développeurs** or visit https://developers.nimbasms.com for API documentation
4. Copy your **Service ID** and **Secret Token**
5. Register and get your **Sender Name** approved (usually takes 24-48 hours)
6. Add credits to your account

Step 2: Configure in Odoo
~~~~~~~~~~~~~~~~~~~~~~~~~

1. Go to **Settings → General Settings**
2. Scroll to the **SMS** section
3. Select **"Nimba SMS"** as your SMS Provider
4. Click the **"Manage Account"** button
5. Enter your **Service ID**, **Secret Token**, and **Sender Name**
6. Click **"Test Connection"** to verify your credentials
7. Click **"Save"** to apply the configuration

Usage
-----

Sending SMS
~~~~~~~~~~~

Once configured, you can send SMS from anywhere in Odoo:

* **From Contacts**: Open any contact record and click the SMS icon
* **From Marketing Campaigns**: Create SMS marketing campaigns and send to multiple recipients
* **From Other Modules**: Any module that supports SMS functionality (Sales, CRM, Events, etc.)

Phone Number Format
~~~~~~~~~~~~~~~~~~~

Phone numbers should be in international E.164 format:

* ✅ **Correct**: ``+224620000000`` (Guinea)
* ✅ **Correct**: ``624000000`` (Guinea, auto-formatted)

The module automatically formats numbers when possible.

Webhook Configuration (Optional)
--------------------------------

Webhooks enable real-time delivery status updates from Nimba SMS to Odoo.

Setup:

1. Get your webhook URL: ``https://your-odoo-domain.com/sms/webhook/nimba``
2. Log in to https://www.nimbasms.com
3. Navigate to **API → Webhooks**
4. Enter your webhook URL and save

**Note**: Webhooks work automatically across all databases in multi-tenant setups.

Requirements
------------

* Odoo 19.0 or higher
* Python packages: ``nimbasms``, ``phonenumbers``
* Nimba SMS account (sign up at https://www.nimbasms.com)

Troubleshooting
--------------

Common Issues
~~~~~~~~~~~~~~

* **SDK not installed**: Run ``pip install nimbasms phonenumbers`` and restart Odoo
* **Invalid credentials**: Double-check Service ID and Secret Token in Dashboard → Développeurs
* **Invalid Sender Name**: Ensure Sender Name is approved and spelling matches exactly
* **Insufficient balance**: Top up your Nimba SMS account
* **Invalid phone number**: Use international format: ``+224620000000``

Check Logs
~~~~~~~~~~

Go to **Settings → Technical → Logging** and filter by "nimba" or "sms" to see error messages.

Support
-------

* Email: support@nimbasms.com
* Website: https://www.nimbasms.com
* API Documentation: https://developers.nimbasms.com

