# app.py

import os
from flask import Flask, render_template, redirect, url_for, session, request
from google_auth_oauthlib.flow import Flow
import gmail_helper

app = Flask(__name__)
# This secret key is required for Flask session management
app.secret_key = 'your-super-secret-key-change-me' 

# This ensures the redirect URI is HTTPS in production, but allows HTTP for local development.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

def get_google_auth_flow():
    """Initializes the Google OAuth 2.0 flow."""
    flow = Flow.from_client_secrets_file(
        gmail_helper.CREDENTIALS_FILE,
        scopes=gmail_helper.SCOPES,
        redirect_uri=url_for('oauth2callback', _external=True)
    )
    return flow

@app.route('/')
def index():
    """Renders the main page."""
    # Check if token.json exists to determine auth status
    is_authorized = os.path.exists(gmail_helper.TOKEN_FILE)
    return render_template('index.html', is_authorized=is_authorized)

@app.route('/authorize')
def authorize():
    """Redirects the user to Google's authorization page."""
    flow = get_google_auth_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    # Store the state in the session to verify on callback
    session['state'] = state
    return redirect(authorization_url)

@app.route('/callback')
def oauth2callback():
    """Handles the callback from Google after authorization."""
    # Verify the state to protect against CSRF attacks
    state = session['state']
    flow = get_google_auth_flow()
    flow.fetch_token(authorization_response=request.url, state=state)

    # Store the credentials in a file
    credentials = flow.credentials
    with open(gmail_helper.TOKEN_FILE, 'w') as token_file:
        token_file.write(credentials.to_json())

    return redirect(url_for('index'))

@app.route('/fetch_emails', methods=['POST'])
def fetch_emails():
    """Fetches email summaries and displays them."""
    summaries = gmail_helper.get_email_summaries()
    is_authorized = os.path.exists(gmail_helper.TOKEN_FILE)
    
    # Handle both successful fetches and error messages
    if isinstance(summaries, str):
        return render_template('index.html', is_authorized=is_authorized, error=summaries)
    else:
        return render_template('index.html', is_authorized=is_authorized, emails=summaries)

@app.route('/logout')
def logout():
    """Clears the session and deletes the token file."""
    if os.path.exists(gmail_helper.TOKEN_FILE):
        os.remove(gmail_helper.TOKEN_FILE)
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Using port 8080 to match the redirect URI in credentials.json
    app.run(port=8080, debug=True)