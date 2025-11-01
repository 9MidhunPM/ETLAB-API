import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AppConfig:
    """Application configuration class"""
    
    def __init__(self):
        # Server Configuration
        self.port = int(os.getenv('PORT', '3000'))
        
        # Application Configuration
        self.base_url = os.getenv('APP_BASE_URL', 'https://sahrdaya.etlab.in')
        self.cookie_key = os.getenv('APP_COOKIE_KEY', 'SAHRDAYASESSIONID')
        self.user_agent = os.getenv('APP_USER_AGENT', 
                                   'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36')
        
        # CORS Configuration
        self.cors_allowed_origins = os.getenv('CORS_ALLOWED_ORIGINS', '*')
        self.cors_allowed_methods = os.getenv('CORS_ALLOWED_METHODS', 'GET,POST,PUT,DELETE,OPTIONS')
        self.cors_allowed_headers = os.getenv('CORS_ALLOWED_HEADERS', '*')
        self.cors_allow_credentials = os.getenv('CORS_ALLOW_CREDENTIALS', 'true').lower() == 'true'
        
        # Logging Configuration
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        
        # Cloudflare Bypass Configuration
        self.cloudflare_bypass_enabled = os.getenv('CLOUDFLARE_BYPASS_ENABLED', 'true').lower() == 'true'
        self.cloudflare_max_retries = int(os.getenv('CLOUDFLARE_MAX_RETRIES', '3'))
        self.cloudflare_retry_delay = int(os.getenv('CLOUDFLARE_RETRY_DELAY', '5'))
        self.selenium_headless = os.getenv('SELENIUM_HEADLESS', 'true').lower() == 'true'
        self.selenium_timeout = int(os.getenv('SELENIUM_TIMEOUT', '30'))
        self.cloudscraper_delay = int(os.getenv('CLOUDSCRAPER_DELAY', '10'))
        
        # Request Configuration
        self.request_timeout = int(os.getenv('REQUEST_TIMEOUT', '30'))
        self.max_request_retries = int(os.getenv('MAX_REQUEST_RETRIES', '3'))

# Global config instance
config = AppConfig()