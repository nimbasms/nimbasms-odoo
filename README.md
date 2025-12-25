# Nimba SMS Provider for Odoo

Send SMS directly from Odoo using [Nimba SMS](https://nimbasms.com), a reliable SMS provider with coverage across Guinea and other African countries.

## Features

- **Batch Sending** - Send to multiple recipients in one request With Sms Marketing
- **Delivery Tracking** - Real-time delivery status updates via webhooks
- **Easy Configuration** - Simple setup via Odoo Settings interface
- **Error Handling** - Clear error messages and troubleshooting

## Prerequisites

- Odoo 19.0 or higher
- Python packages: `nimbasms`, `phonenumbers`
- Nimba SMS account ([sign up here](https://nimbasms.com))

## Installation

### 1. Add Module to Odoo

Place the module in your Odoo addons directory. There are several ways to do this:

**Option A: Copy to addons directory**
```bash
# Copy module to Odoo addons path
cp -r nimbasms /path/to/odoo/addons/
```

**Option B: Use extra-addons directory**
```bash
# Create extra-addons directory if it doesn't exist
mkdir -p /path/to/extra-addons

# Copy or link module
cp -r nimbasms /path/to/extra-addons/
# OR symlink it
ln -s /path/to/nimbasms /path/to/extra-addons/nimbasms
```

Then add the path to your Odoo configuration file (`odoo.conf`):
```ini
[options]
addons_path = /path/to/odoo/addons,/path/to/extra-addons
```

Or start Odoo with the `--addons-path` parameter:
```bash
odoo-bin --addons-path=/path/to/odoo/addons,/path/to/extra-addons
```

### 2. Install Python Dependencies

Install the required Python packages:

```bash
pip install nimbasms phonenumbers
```

### 3. Install the Module in Odoo

1. **Restart Odoo** to detect the new module
2. Go to **Apps** menu (enable Developer Mode if needed)
3. Click **Update Apps List**
4. Search for **"Nimba SMS"**
5. Click **Install**

## Configuration

### Step 1: Get Your Nimba SMS Credentials

1. **Sign Up**
   - Visit [nimbasms.com](https://nimbasms.com) and create an account

2. **Get API Credentials**
   - Log in to your Nimba SMS dashboard
   - Click on **"Développeurs"** (Developers) in the left menu
   - You will find your API credentials:
     - **Service ID** (`service_id`) - Unique identifier for your client application
     - **Secret Token** (`secret_token`) - Secret known only by your application and the authorization server

3. **Register Your Sender Name**
   - Go to **Sender Names** section in the dashboard
   - Register your desired sender name (e.g., "MyCompany", "MYAPP")
   - Wait for approval (usually 24-48 hours)

4. **Add Credits**
   - Top up your account with credits for sending SMS

### Step 2: Configure in Odoo

1. **Navigate to SMS Settings**
   - Go to **Settings** → **General Settings**
   - Scroll to the **SMS** section

2. **Select Provider**
   - Choose **"Nimba SMS"** as your SMS Provider

3. **Enter Credentials**
   - Click the **"Manage Account"** button
   - A configuration wizard will open
   - **Service ID**: Enter your **Service ID** from Nimba dashboard (found in Développeurs)
   - **Secret Token**: Enter your **Secret Token** from Nimba dashboard (found in Développeurs)
   - **Sender Name**: Enter your approved sender name

4. **Test Connection**
   - Click **"Test Connection"** button
   - You should see a success message with your account balance

5. **Save**
   - Click **"Save"** to apply the configuration

## Usage

### Sending SMS from Odoo

**From Contacts:**
1. Open any contact record
2. Click the **SMS icon** or **Actions → Send SMS**
3. Type your message
4. Click **Send**

**From Marketing Campaigns:**
1. Create or open an SMS Marketing campaign
2. Select your target audience
3. Compose your message
4. Send to all recipients

**From Other Modules:**
- SMS can be sent from any module that supports SMS functionality (Sales, CRM, Events, etc.)
- Look for the SMS icon or "Send SMS" action

### Checking SMS Status

SMS records can be viewed in:
- **SMS Menu** (if installed)
- **Technical → SMS → SMS**

Status values:
- **Outgoing**: Queued for sending
- **Sent**: Successfully delivered
- **Error**: Failed to send (check error message)

## Webhook Configuration (Optional)

Webhooks enable real-time delivery status updates from Nimba SMS to Odoo.

### Setup

1. **Get Your Webhook URL**
   ```
   https://your-odoo-domain.com/sms/webhook/nimba
   ```
   Replace `your-odoo-domain.com` with your actual Odoo URL.

2. **Configure in Nimba SMS Dashboard**
   - Log in to [Nimba SMS Portal](https://portal.nimbasms.com)
   - Navigate to **API → Webhooks**
   - Enter your webhook URL
   - Click **Save**

3. **Verify**
   - Send a test SMS from Odoo
   - Check that the status updates to "Sent" after delivery

**Note**: Webhooks work automatically across all databases in multi-tenant setups.

## Troubleshooting

### SMS Not Sending

**Check Configuration:**
- Verify your Service ID and Secret Token are correct
- Ensure your Sender Name is approved by Nimba SMS
- Confirm you have sufficient account balance

**Test Connection:**
- Go to Settings → SMS → Nimba SMS
- Click "Manage Account"
- Click "Test Connection" button

**Check Logs:**
- Go to Settings → Technical → Logging
- Filter by "nimba" or "sms" to see error messages

### Common Errors

| Error | Solution |
|-------|----------|
| "SDK not installed" | Run `pip install nimbasms phonenumbers` and restart Odoo |
| "Invalid credentials" | Double-check Service ID and Secret Token in Dashboard → Développeurs |
| "Invalid Sender Name" | Ensure Sender Name is approved; check spelling matches exactly |
| "Insufficient balance" | Top up your Nimba SMS account |
| "Invalid phone number" | Use international format: `+224620000000` |

### Phone Number Format

Always use international E.164 format:
- ✅ **Correct**: `+224620000000` (Guinea)
- ✅ **Correct**: `624000000` (Guinea)

The module auto-formats numbers when possible, but explicit international format is recommended.

### Webhook Not Working

1. **Verify URL is accessible** - Test from outside your network
2. **Check webhook is configured** in Nimba SMS dashboard
3. **Ensure HTTPS** is enabled in production (required for security)
4. **Check Odoo logs** for webhook-related errors

## Support

### Getting Help

- **Module Issues**: [GitHub Issues](https://github.com/nimbasms/nimbasms-odoo/issues)
- **Nimba SMS Support**: [nimbasms.com/support](https://nimbasms.com/support)
- **Odoo Community**: [Odoo Community Forum](https://www.odoo.com/forum)

### Reporting Bugs

When reporting issues, please include:
- Odoo version
- Module version
- Error message (from Odoo logs)
- Steps to reproduce

## License

LGPL-3 (same as Odoo)

## Credits

- **Author**: Nimba SMS Integration Team
- **Maintainer**: Nimba SMS
- **Website**: [nimbasms.com](https://nimbasms.com)
- **Repository**: [github.com/nimbasms/nimbasms-odoo](https://github.com/nimbasms/nimbasms-odoo)

---

**Version**: 1.0.0
**Compatible with**: Odoo 19.0
**Last Updated**: November 2025
