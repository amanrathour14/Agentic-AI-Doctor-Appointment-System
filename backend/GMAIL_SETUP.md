# Gmail API OAuth2 Setup Guide

This guide explains how to set up Gmail API integration with OAuth2 authentication for the MedAI Assistant system.

## Prerequisites

1. Google Cloud Platform account
2. Gmail API enabled
3. OAuth2 credentials configured

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your project ID

## Step 2: Enable Gmail API

1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Gmail API"
3. Click on it and press "Enable"

## Step 3: Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Choose "External" user type
3. Fill in the required information:
   - App name: `MedAI Assistant`
   - User support email: Your email
   - Developer contact information: Your email
4. Add scopes:
   - `https://www.googleapis.com/auth/gmail.send`
   - `https://www.googleapis.com/auth/gmail.compose`
   - `https://www.googleapis.com/auth/gmail.modify`
5. Add test users (your email address)
6. Save and continue

## Step 4: Create OAuth2 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Desktop application"
4. Give it a name: `MedAI Gmail Client`
5. Click "Create"
6. Download the JSON file and save it securely

## Step 5: Generate Refresh Token

1. Install the required Python packages:
   ```bash
   pip install google-auth-oauthlib google-auth-httplib2
   ```

2. Run the OAuth2 flow script:
   ```python
   from google_auth_oauthlib.flow import InstalledAppFlow
   from google.auth.transport.requests import Request
   import pickle
   import os

   SCOPES = [
       'https://www.googleapis.com/auth/gmail.send',
       'https://www.googleapis.com/auth/gmail.compose',
       'https://www.googleapis.com/auth/gmail.modify'
   ]

   def get_gmail_credentials():
       creds = None
       
       # Check if token file exists
       if os.path.exists('token.pickle'):
           with open('token.pickle', 'rb') as token:
               creds = pickle.load(token)
       
       # If no valid credentials, let user log in
       if not creds or not creds.valid:
           if creds and creds.expired and creds.refresh_token:
               creds.refresh(Request())
           else:
               flow = InstalledAppFlow.from_client_secrets_file(
                   'path/to/your/credentials.json', SCOPES)
               creds = flow.run_local_server(port=0)
           
           # Save credentials for next run
           with open('token.pickle', 'wb') as token:
               pickle.dump(creds, token)
       
       return creds

   if __name__ == '__main__':
       creds = get_gmail_credentials()
       print(f"Access Token: {creds.token}")
       print(f"Refresh Token: {creds.refresh_token}")
   ```

3. Run the script and authorize the application
4. Copy the refresh token

## Step 6: Configure Environment Variables

Add to your `.env` file:

```env
# Gmail OAuth2 Configuration
GMAIL_CLIENT_ID=your_client_id_from_json
GMAIL_CLIENT_SECRET=your_client_secret_from_json
GMAIL_REFRESH_TOKEN=your_refresh_token_from_script
GMAIL_USER_EMAIL=your_email@gmail.com
```

## Step 7: Test Gmail Integration

Run the backend server and check the API status:

```bash
curl http://localhost:8001/api/status
```

You should see:
```json
{
  "gmail_api": {
    "available": true,
    "status": "connected"
  }
}
```

## Troubleshooting

### Common Issues

1. **"Invalid client" error**
   - Check that client ID and secret are correct
   - Ensure OAuth consent screen is configured

2. **"Access denied" error**
   - Add your email to test users in OAuth consent screen
   - Check that required scopes are added

3. **"Token expired" error**
   - Refresh tokens don't expire, but access tokens do
   - The system automatically refreshes access tokens

### Testing Gmail Integration

You can test the Gmail integration by sending a test email through the chat interface:

```
"Send a test email to john@example.com with subject 'Test' and body 'This is a test email'"
```

If successful, you should see the email in the recipient's inbox.

## Security Notes

- Keep your OAuth2 credentials secure
- Don't commit the credentials JSON file to version control
- Use environment variables for sensitive configuration
- Regularly monitor API usage in Google Cloud Console
- Consider implementing rate limiting to prevent abuse

## API Usage Limits

- Gmail API: 1 billion queries per day
- Per user per second: 250 queries
- Per user per 100 seconds: 1,000 queries

## Next Steps

After setting up Gmail API:
1. Test email sending functionality
2. Configure email templates
3. Set up automated email notifications
4. Monitor email delivery rates