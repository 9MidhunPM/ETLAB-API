"""
Login service - handles authentication logic
"""
from typing import Optional, Tuple
from bs4 import BeautifulSoup
import re
import logging
from app.config.config import config

logger = logging.getLogger(__name__)


class LoginService:
    """
    Service for handling user authentication
    """
    
    @staticmethod
    def validate_credentials(username: Optional[str], password: Optional[str]) -> Tuple[bool, Optional[str]]:
        """
        Validate login credentials
        
        Args:
            username: Username
            password: Password
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not username or not password:
            return False, "Username and password are required"
        
        if len(username.strip()) == 0:
            return False, "Username cannot be empty"
        
        if len(password.strip()) == 0:
            return False, "Password cannot be empty"
        
        return True, None
    
    @staticmethod
    def prepare_login_data(username: str, password: str) -> dict:
        """
        Prepare login form data
        
        Args:
            username: Username
            password: Password
        
        Returns:
            Dictionary with form data
        """
        return {
            'LoginForm[username]': username,
            'LoginForm[password]': password,
            'yt0': ''
        }
    
    @staticmethod
    def check_login_success(html: str) -> bool:
        """
        Check if login was successful by analyzing HTML response
        
        Args:
            html: HTML response content
        
        Returns:
            True if login successful, False otherwise
        """
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('title')
        
        # If still on login page, login failed
        if title and 'login' in title.get_text().lower():
            return False
        
        return True
    
    @staticmethod
    def extract_session_cookie(response) -> Optional[str]:
        """
        Extract session cookie from response
        
        Args:
            response: HTTP response object
        
        Returns:
            Session cookie value or None
        """
        session_cookie = None
        
        # Method 1: Try to get from response cookies
        if hasattr(response, 'cookies') and response.cookies:
            for cookie_name, cookie_value in response.cookies.items():
                if cookie_name == config.cookie_key:
                    session_cookie = cookie_value
                    logger.info(f"Found session cookie in response.cookies")
                    break
        
        # Method 2: If not found, try from Set-Cookie header
        if not session_cookie and 'Set-Cookie' in response.headers:
            set_cookie_header = response.headers.get('Set-Cookie', '')
            pattern = f"{config.cookie_key}=([^;]+)"
            match = re.search(pattern, set_cookie_header)
            if match:
                session_cookie = match.group(1)
                logger.info(f"Found session cookie in Set-Cookie header")
        
        if not session_cookie:
            logger.error("No session cookie found in response")
        
        return session_cookie
