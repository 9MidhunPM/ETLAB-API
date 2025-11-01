import requests
from typing import Optional
import logging
from app.config.config import config

logger = logging.getLogger(__name__)

class HttpService:
    """HTTP service for making requests with Cloudflare bypass capabilities"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.user_agent
        })
        self.cloudflare_bypass = None
        self._init_cloudflare_bypass()
    
    def _decode_response_content(self, response: requests.Response) -> str:
        """
        Properly decode response content, handling various compression formats
        
        Args:
            response: The response object to decode
            
        Returns:
            Decoded text content
        """
        try:
            # Try to use response.text first (requests handles most cases automatically)
            try:
                if response.encoding is None:
                    response.encoding = response.apparent_encoding or 'utf-8'
                
                text = response.text
                
                # Check if it looks like valid HTML/text
                if text and len(text) > 10 and '<' in text[:100]:
                    return text
                    
            except Exception as text_error:
                pass
            
            # If that didn't work, try raw content decoding
            content = response.content
            
            # Try brotli decompression (common with Cloudflare)
            try:
                import brotli
                decoded = brotli.decompress(content).decode('utf-8')
                return decoded
            except ImportError:
                pass
            except Exception:
                pass
            
            # Try gzip decompression
            import gzip
            try:
                decoded = gzip.decompress(content).decode('utf-8')
                return decoded
            except Exception:
                pass
            
            # Try zlib/deflate
            import zlib
            try:
                decoded = zlib.decompress(content).decode('utf-8')
                return decoded
            except Exception:
                pass
            
            # Last resort: direct decode with error handling
            try:
                decoded = content.decode('utf-8', errors='replace')
                return decoded
            except Exception as decode_error:
                logger.error(f"All decoding methods failed: {decode_error}")
                return str(content[:1000])
            
        except Exception as e:
            logger.error(f"Critical error in _decode_response_content: {e}")
            return str(response.content[:1000])
    
    def _init_cloudflare_bypass(self):
        """Initialize Cloudflare bypass service if enabled"""
        try:
            if getattr(config, 'cloudflare_bypass_enabled', True):
                from app.services.cloudflare_bypass_service import CloudflareBypassService
                self.cloudflare_bypass = CloudflareBypassService(config)
        except Exception as e:
            logger.error(f"Failed to initialize Cloudflare bypass: {e}")
    
    def get(self, url: str, token: Optional[str] = None) -> str:
        """
        Make a GET request to the specified URL with optional token and Cloudflare bypass
        
        Args:
            url: The URL to make the request to
            token: Optional session token for authentication
            
        Returns:
            Response text content
            
        Raises:
            Exception: If the request fails
        """
        try:
            headers = {}
            cookies = {}
            
            if token:
                cookies[config.cookie_key] = token
                headers['Cookie'] = f"{config.cookie_key}={token}"
            
            # Try Cloudflare bypass first if available
            if self.cloudflare_bypass:
                response = self.cloudflare_bypass.bypass_cloudflare(
                    url=url, 
                    method='GET',
                    headers=headers,
                    cookies=cookies
                )
                
                if response and response.status_code == 200:
                    return self._decode_response_content(response)
            
            # Fallback to standard request
            
            # Update session cookies if token provided
            if token:
                self.session.cookies.set(config.cookie_key, token)
            
            response = self.session.get(url, headers=headers, cookies=cookies, timeout=30)
            response.raise_for_status()
            
            # Decode response content properly
            content = self._decode_response_content(response)
            
            # Check if response indicates Cloudflare block
            if self._is_cloudflare_blocked(content):
                raise Exception("Request blocked by Cloudflare protection")
            
            return content
            
        except requests.RequestException as e:
            logger.error(f"HTTP GET request failed for URL {url}: {e}")
            raise Exception(f"HTTP request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Request failed with error: {e}")
            raise
    
    def post(self, url: str, data: dict = None, headers: dict = None, token: Optional[str] = None) -> requests.Response:
        """
        Make a POST request to the specified URL with Cloudflare bypass
        
        Args:
            url: The URL to make the request to
            data: Form data to send
            headers: Additional headers
            token: Optional session token for authentication
            
        Returns:
            Response object
            
        Raises:
            Exception: If the request fails
        """
        try:
            request_headers = headers or {}
            cookies = {}
            
            if token:
                cookies[config.cookie_key] = token
                request_headers['Cookie'] = f"{config.cookie_key}={token}"
            
            # Try Cloudflare bypass first if available
            if self.cloudflare_bypass:
                response = self.cloudflare_bypass.bypass_cloudflare(
                    url=url, 
                    method='POST',
                    data=data,
                    headers=request_headers,
                    cookies=cookies
                )
                
                if response and response.status_code == 200:
                    return response
            
            # Fallback to standard request
            
            # Update session cookies if token provided
            if token:
                self.session.cookies.set(config.cookie_key, token)
            
            response = self.session.post(url, data=data, headers=request_headers, cookies=cookies, timeout=30)
            response.raise_for_status()
            
            # Check if response indicates Cloudflare block
            if self._is_cloudflare_blocked(response.text):
                raise Exception("Request blocked by Cloudflare protection")
            
            return response
            
        except requests.RequestException as e:
            logger.error(f"HTTP POST request failed for URL {url}: {e}")
            raise Exception(f"HTTP request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Request failed with error: {e}")
            raise
    
    def _is_cloudflare_blocked(self, content: str) -> bool:
        """Check if the response indicates Cloudflare challenge blocking"""
        if not content:
            return False
        
        # More specific challenge indicators (not just CDN references)
        challenge_indicators = [
            'Checking your browser',
            'DDoS protection by Cloudflare',
            'cf-browser-verification',
            'cf-challenge-form',
            '__cf_chl_jschl_tk__',
            'cf-challenge-running',
            'challenge-platform',
            'Enable JavaScript and cookies to continue'
        ]
        
        content_lower = content.lower()
        
        # Check for actual challenge indicators
        for indicator in challenge_indicators:
            if indicator.lower() in content_lower:
                return True
        
        # Check if title contains Cloudflare challenge keywords
        if '<title>' in content_lower:
            title_start = content_lower.find('<title>')
            title_end = content_lower.find('</title>', title_start)
            if title_start != -1 and title_end != -1:
                title = content_lower[title_start:title_end]
                if 'cloudflare' in title and ('checking' in title or 'please wait' in title or 'attention' in title):
                    return True
        
        return False
    
    def get_bypass_cookies(self) -> dict:
        """Get cookies from successful Cloudflare bypass"""
        if self.cloudflare_bypass:
            return self.cloudflare_bypass.get_session_cookies()
        return {}
    
    def close(self):
        """Close the session and cleanup bypass service"""
        if self.session:
            self.session.close()
        
        if self.cloudflare_bypass:
            self.cloudflare_bypass.close()

# Global instance
http_service = HttpService()