# Google OAuth Login Setup Guide

This guide will help you set up Google OAuth authentication for your Flask app.

## Step 1: Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API:
   - In the left sidebar, go to **APIs & Services** → **Library**
   - Search for "Google+ API"
   - Click on it and click **Enable**

4. Create OAuth 2.0 Credentials:
   - Go to **APIs & Services** → **Credentials**
   - Click **Create Credentials** → **OAuth Client ID**
   - Choose **Web application**
   - Add authorized JavaScript origins:
     - `http://localhost:5000` (for local development)
     - Your production domain (e.g., `https://yourapp.com`)
   - Add authorized redirect URIs:
     - `http://localhost:5000/auth/google`
     - `https://yourapp.com/auth/google`
   - Click **Create**

5. Copy your **Client ID** and **Client Secret**

## Step 2: Update Environment Variables

Edit your `.env` file and add:

```env
GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret-here
SECRET_KEY=your-secret-key-here-change-in-production
```

## Step 3: Install Dependencies

Run the following command to install the required packages:

```bash
pip install -r requirements.txt
```

The new dependencies added are:
- `Flask-Login` - For user session management
- `google-auth-oauthlib` - For Google OAuth authentication
- `google-auth-httplib2` - Required by google-auth

## Step 4: Update Database

Your `Student` model now includes a `google_id` field. Run migrations or recreate the database:

```bash
# Using Flask shell
from app import app, db
with app.app_context():
    db.create_all()
```

## Step 5: Test It Out

1. Start your Flask application:
   ```bash
   python app.py
   ```

2. Go to `http://localhost:5000/login`

3. You should see a Google Sign-In button below the email/password form

4. Click the button and sign in with your Google account

## How It Works

1. User clicks the Google Sign-In button
2. Google's JavaScript library handles the OAuth flow
3. User authenticates with Google and gets a token
4. The token is sent to your `/auth/google` endpoint
5. Your backend verifies the token with Google
6. User is created or logged in based on their email
7. User is redirected to the dashboard

## Features

- **Auto Sign-Up**: Users can sign up by signing in with Google
- **Account Linking**: If a user has an existing account with the same email, their Google account is linked
- **No Password Required**: Users can sign in without setting a password
- **Secure**: All tokens are verified with Google's servers

## Troubleshooting

### "Invalid Client ID" Error
- Make sure `GOOGLE_CLIENT_ID` is set correctly in `.env`
- Make sure the domain is in the authorized JavaScript origins

### "Redirect URI mismatch" Error
- Add `http://localhost:5000` to authorized JavaScript origins in Google Cloud Console

### Users not logging in
- Check browser console (F12) for JavaScript errors
- Make sure `google-auth-oauthlib` is installed: `pip list | grep google`
- Check Flask server logs for any errors

## Production Notes

1. Always use HTTPS in production
2. Set a strong `SECRET_KEY` in `.env`
3. Update the authorized origins and redirect URIs to your production domain
4. Keep your `GOOGLE_CLIENT_SECRET` secure (don't commit it to version control)
5. Use environment variables from your hosting provider instead of `.env` files
