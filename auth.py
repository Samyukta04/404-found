import streamlit as st
import requests
import urllib.parse
import secrets
import time
from datetime import datetime, timedelta
from config import Config


class GoogleOAuth:
    def __init__(self):
        Config.validate_config()
        self.client_id = Config.GOOGLE_CLIENT_ID
        self.client_secret = Config.GOOGLE_CLIENT_SECRET
        self.redirect_uri = Config.GOOGLE_REDIRECT_URI
        self.auth_url = Config.GOOGLE_AUTH_URL
        self.token_url = Config.GOOGLE_TOKEN_URL
        self.user_info_url = Config.GOOGLE_USER_INFO_URL
        self.scopes = Config.GOOGLE_SCOPES

    def get_auth_url(self):
        """Generate Google OAuth authorization URL"""
        state = secrets.token_urlsafe(32)
        st.session_state.oauth_state = state

        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(self.scopes),
            'response_type': 'code',
            'state': state,
            'access_type': 'offline',
            'prompt': 'consent'
        }

        return f"{self.auth_url}?{urllib.parse.urlencode(params)}"

    def exchange_code_for_token(self, code, state):
        """Exchange authorization code for access token"""
        if state != st.session_state.get('oauth_state'):
            raise ValueError("Invalid state parameter")

        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        }

        response = requests.post(self.token_url, data=data)
        response.raise_for_status()

        return response.json()

    def get_user_info(self, access_token):
        """Get user information from Google"""
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(self.user_info_url, headers=headers)
        response.raise_for_status()

        return response.json()

    def is_admin_user(self, email):
        """Check if user is admin"""
        return email in Config.ADMIN_EMAILS

    def login_user(self, user_info, access_token):
        """Log in user and store session information"""
        st.session_state.authenticated = True
        st.session_state.user_info = user_info
        st.session_state.access_token = access_token
        st.session_state.login_time = datetime.now()
        st.session_state.is_admin = self.is_admin_user(user_info.get('email', ''))

    def logout_user(self):
        """Log out user and clear session"""
        keys_to_clear = [
            'authenticated', 'user_info', 'access_token',
            'login_time', 'is_admin', 'oauth_state'
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]

    def is_session_valid(self):
        """Check if current session is still valid"""
        if not st.session_state.get('authenticated', False):
            return False

        login_time = st.session_state.get('login_time')
        if login_time and datetime.now() - login_time > timedelta(hours=24):
            self.logout_user()
            return False

        return True


def render_login_page():
    """Render the login page"""
    st.markdown("""
    <div style="
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 80vh;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        border-radius: 20px;
        color: white;
        text-align: center;
        margin: 2rem 0;
        padding: 3rem;
    ">
        <h1 style="font-size: 3.5rem; margin-bottom: 1rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
            🧠 Synchrony Credit Intelligence
        </h1>
        <h2 style="font-size: 1.8rem; margin-bottom: 2rem; opacity: 0.9; font-weight: 300;">
            AI-Powered Credit Optimization Platform
        </h2>
        <div style="
            background: rgba(255,255,255,0.1);
            padding: 2rem;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        ">
            <h3 style="margin-bottom: 1rem;">🔐 Secure Access Required</h3>
            <p style="font-size: 1.1rem; opacity: 0.9; line-height: 1.6;">
                This platform contains sensitive financial data and requires<br>
                authenticated access via Google OAuth for security compliance.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Create three columns for centering
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        oauth = GoogleOAuth()
        auth_url = oauth.get_auth_url()

        st.markdown(f"""
        <div style="text-align: center; margin: 2rem 0;">
            <a href="{auth_url}" target="_self" style="text-decoration: none;">
                <button style="
                    background: linear-gradient(135deg, #4285f4 0%, #34a853 50%, #ea4335 100%);
                    color: white;
                    border: none;
                    padding: 1rem 3rem;
                    font-size: 1.2rem;
                    font-weight: 600;
                    border-radius: 50px;
                    cursor: pointer;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                    transition: transform 0.3s ease;
                    display: inline-flex;
                    align-items: center;
                    gap: 1rem;
                ">
                    <svg width="20" height="20" viewBox="0 0 24 24">
                        <path fill="white" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                        <path fill="white" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                        <path fill="white" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                        <path fill="white" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                    </svg>
                    Sign in with Google
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)

        # Demo credentials info
        st.info("""
        **🎭 For Demo Purposes:**

        Use any Google account to log in. For admin features, configure your email in the `.env` file under `ADMIN_EMAILS`.

        **Features after login:**
        - Full access to Credit Intelligence Engine
        - Real-time customer portfolio management  
        - AI-powered credit optimization
        - Live market data integration
        """)


def render_user_header():
    """Render user information in header"""
    if st.session_state.get('authenticated', False):
        user_info = st.session_state.get('user_info', {})

        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            user_name = user_info.get('name', 'User')
            user_email = user_info.get('email', '')
            is_admin = st.session_state.get('is_admin', False)
            admin_badge = " 👑" if is_admin else ""

            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                color: white;
                padding: 1rem;
                border-radius: 10px;
                margin-bottom: 1rem;
            ">
                <h4 style="margin: 0;">Welcome, {user_name}{admin_badge}</h4>
                <p style="margin: 0; opacity: 0.9; font-size: 0.9rem;">{user_email}</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            login_time = st.session_state.get('login_time')
            if login_time:
                session_duration = datetime.now() - login_time
                hours = int(session_duration.total_seconds() // 3600)
                minutes = int((session_duration.total_seconds() % 3600) // 60)
                st.metric("Session", f"{hours}h {minutes}m")

        with col3:
            if st.button("🚪 Logout", type="secondary"):
                oauth = GoogleOAuth()
                oauth.logout_user()
                st.rerun()


def handle_oauth_callback():
    """Handle OAuth callback from Google"""
    query_params = st.experimental_get_query_params()

    if 'code' in query_params and 'state' in query_params:
        code = query_params['code'][0]
        state = query_params['state'][0]

        try:
            oauth = GoogleOAuth()
            token_data = oauth.exchange_code_for_token(code, state)
            access_token = token_data['access_token']

            user_info = oauth.get_user_info(access_token)
            oauth.login_user(user_info, access_token)

            # Clear query params after successful login
            st.experimental_set_query_params()
            st.success(f"✅ Successfully logged in as {user_info.get('name', 'User')}")
            time.sleep(1)
            st.rerun()

        except Exception as e:
            st.error(f"❌ Login failed: {str(e)}")
            st.info("Please try logging in again.")
            oauth = GoogleOAuth()
            oauth.logout_user()


def require_authentication(func):
    """Decorator to require authentication for functions"""

    def wrapper(*args, **kwargs):
        oauth = GoogleOAuth()

        if not oauth.is_session_valid():
            render_login_page()
            return None

        return func(*args, **kwargs)

    return wrapper
