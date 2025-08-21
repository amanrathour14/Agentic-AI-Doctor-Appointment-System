# Google Calendar API Setup Guide

This guide explains how to set up Google Calendar API integration for the MedAI Assistant system.

## Prerequisites

1. Google Cloud Platform account
2. Google Calendar API enabled
3. Service Account credentials

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your project ID

## Step 2: Enable Google Calendar API

1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google Calendar API"
3. Click on it and press "Enable"

## Step 3: Create Service Account

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in the service account details:
   - Name: `medai-calendar-service`
   - Description: `Service account for MedAI Assistant calendar integration`
4. Click "Create and Continue"
5. Skip role assignment for now (click "Continue")
6. Click "Done"

## Step 4: Generate Service Account Key

1. In the Credentials page, find your service account
2. Click on the service account email
3. Go to the "Keys" tab
4. Click "Add Key" > "Create New Key"
5. Select "JSON" format
6. Download the JSON file
7. Save it securely (e.g., `google-credentials.json`)

## Step 5: Share Calendar with Service Account

1. Open Google Calendar
2. Go to "Settings" > "Settings for my calendars"
3. Select the calendar you want to use
4. Go to "Share with specific people"
5. Add the service account email (from the JSON file)
6. Give it "Make changes to events" permission
7. Click "Send"

## Step 6: Configure Environment Variables

Add to your `.env` file:

\`\`\`env
GOOGLE_CALENDAR_CREDENTIALS=/path/to/google-credentials.json
\`\`\`

## Step 7: Test Integration

Run the backend server and check the API status:

\`\`\`bash
curl http://localhost:8000/api/status
\`\`\`

You should see:
\`\`\`json
{
  "google_calendar": {
    "available": true,
    "status": "connected"
  }
}
\`\`\`

## Troubleshooting

### Common Issues

1. **"Calendar not found" error**
   - Make sure you shared the calendar with the service account
   - Check that the service account email is correct

2. **"Insufficient permissions" error**
   - Ensure the service account has "Make changes to events" permission
   - Verify the Google Calendar API is enabled

3. **"Credentials not found" error**
   - Check the path to the credentials file
   - Ensure the JSON file is valid and readable

### Testing Calendar Integration

You can test the calendar integration by scheduling an appointment through the chat interface:

\`\`\`
"I want to book an appointment with Dr. Ahuja tomorrow at 2 PM"
\`\`\`

If successful, you should see a new event in your Google Calendar.

## Security Notes

- Keep your service account credentials secure
- Don't commit the JSON credentials file to version control
- Use environment variables for sensitive configuration
- Regularly rotate service account keys
- Monitor API usage in Google Cloud Console
