# Email Service Setup Guide

This guide explains how to set up email notifications for the MedAI Assistant system.

## Option 1: SendGrid (Recommended)

SendGrid is a reliable email delivery service with good deliverability rates.

### Setup Steps

1. **Create SendGrid Account**
   - Go to [SendGrid](https://sendgrid.com/)
   - Sign up for a free account (100 emails/day)

2. **Create API Key**
   - Go to Settings > API Keys
   - Click "Create API Key"
   - Choose "Restricted Access"
   - Give permissions for "Mail Send"
   - Copy the API key

3. **Verify Sender Identity**
   - Go to Settings > Sender Authentication
   - Verify a single sender email address
   - Or set up domain authentication for better deliverability

4. **Configure Environment Variables**
   \`\`\`env
   SENDGRID_API_KEY=your_sendgrid_api_key_here
   FROM_EMAIL=noreply@yourdomain.com
   \`\`\`

### Testing SendGrid

\`\`\`bash
curl -X POST http://localhost:8000/api/status
\`\`\`

Should show:
\`\`\`json
{
  "email_service": {
    "available": true,
    "status": "connected"
  }
}
\`\`\`

## Option 2: SMTP (Gmail Example)

You can use any SMTP server, including Gmail with App Passwords.

### Gmail Setup

1. **Enable 2-Factor Authentication**
   - Go to Google Account settings
   - Enable 2FA if not already enabled

2. **Generate App Password**
   - Go to Google Account > Security
   - Under "Signing in to Google", select "App passwords"
   - Generate a password for "Mail"
   - Copy the 16-character password

3. **Configure Environment Variables**
   \`\`\`env
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your_email@gmail.com
   SMTP_PASSWORD=your_16_character_app_password
   FROM_EMAIL=your_email@gmail.com
   \`\`\`

### Other SMTP Providers

**Outlook/Hotmail:**
\`\`\`env
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
\`\`\`

**Yahoo:**
\`\`\`env
SMTP_HOST=smtp.mail.yahoo.com
SMTP_PORT=587
\`\`\`

**Custom SMTP:**
\`\`\`env
SMTP_HOST=mail.yourdomain.com
SMTP_PORT=587
SMTP_USER=noreply@yourdomain.com
SMTP_PASSWORD=your_password
\`\`\`

## Email Templates

The system sends two types of emails:

### 1. Patient Confirmation Email
- Sent when appointment is scheduled
- Contains appointment details
- Includes preparation instructions
- Professional medical styling

### 2. Doctor Notification Email
- Sent to doctor when new appointment is booked
- Contains patient information
- Includes symptoms/reason for visit
- System notification styling

## Testing Email Integration

1. **Check API Status**
   \`\`\`bash
   curl http://localhost:8000/api/status
   \`\`\`

2. **Schedule Test Appointment**
   Use the chat interface:
   \`\`\`
   "Book an appointment with Dr. Ahuja tomorrow at 2 PM for John Doe, email john@example.com"
   \`\`\`

3. **Check Email Delivery**
   - Patient should receive confirmation email
   - Doctor should receive notification email
   - Check spam folders if emails don't arrive

## Troubleshooting

### Common Issues

1. **"Authentication failed" (SMTP)**
   - Check username/password
   - Ensure 2FA and app passwords are set up correctly
   - Verify SMTP settings for your provider

2. **"Unauthorized" (SendGrid)**
   - Check API key is correct
   - Verify API key has Mail Send permissions
   - Ensure sender email is verified

3. **Emails going to spam**
   - Set up domain authentication (SendGrid)
   - Use a professional from email address
   - Avoid spam trigger words in subject/content

4. **Rate limiting**
   - SendGrid free: 100 emails/day
   - Gmail: 500 emails/day
   - Consider upgrading for higher volumes

### Email Delivery Best Practices

1. **Use verified sender addresses**
2. **Set up SPF/DKIM records** for your domain
3. **Monitor bounce rates** and unsubscribes
4. **Use professional email templates**
5. **Include unsubscribe links** for marketing emails
6. **Test email rendering** across different clients

## Security Considerations

- Store API keys securely in environment variables
- Use app passwords instead of account passwords
- Regularly rotate API keys and passwords
- Monitor email sending logs for suspicious activity
- Implement rate limiting to prevent abuse
