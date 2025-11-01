import cloudscraper
import requests
import time
import logging
import random
from typing import Optional, Dict, Any
from fake_useragent import UserAgent
import httpx
import socket
import dns.resolver

# Optional imports for advanced bypass methods
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, WebDriverException
    import undetected_chromedriver as uc
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    from requests_html import HTMLSession
    REQUESTS_HTML_AVAILABLE = True
except ImportError:
    REQUESTS_HTML_AVAILABLE = False

logger = logging.getLogger(__name__)

class CloudflareBypassService:
    """
    Comprehensive Cloudflare bypass service with multiple strategies
    """
    
    def __init__(self, config):
        self.config = config
        self.ua = UserAgent()
        self.session = None
        self.driver = None
        self.cloudscraper_session = None
        self._init_sessions()
    
    def _init_sessions(self):
        """Initialize various session types"""
        try:
            # Configure custom DNS resolution using public DNS servers
            self._configure_dns()
            
            # Initialize cloudscraper session
            self.cloudscraper_session = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'mobile': False
                },
                delay=10,
                debug=False
            )
            
            # Initialize requests session with advanced headers
            self.session = requests.Session()
            self._setup_session_headers()
            
        except Exception as e:
            logger.error(f"Failed to initialize bypass sessions: {e}")
    
    def _configure_dns(self):
        """Configure custom DNS resolution using public DNS servers"""
        try:
            # Configure dnspython to use public DNS servers
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [
                '8.8.8.8',      # Google DNS Primary
                '8.8.4.4',      # Google DNS Secondary
                '1.1.1.1',      # Cloudflare DNS Primary
                '1.0.0.1',      # Cloudflare DNS Secondary
            ]
            resolver.timeout = 5
            resolver.lifetime = 10
            
            # Set as default resolver
            dns.resolver.default_resolver = resolver
            
            # Also configure socket-level DNS fallback
            original_getaddrinfo = socket.getaddrinfo
            
            def custom_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
                """Custom DNS resolver with public DNS fallback"""
                try:
                    # Try default system DNS first
                    return original_getaddrinfo(host, port, family, type, proto, flags)
                except socket.gaierror as e:
                    # If system DNS fails, try dnspython with public DNS
                    try:
                        answers = resolver.resolve(host, 'A')
                        if answers:
                            ip = str(answers[0])
                            # Return result in getaddrinfo format
                            return [(socket.AF_INET, socket.SOCK_STREAM, proto, '', (ip, port))]
                    except Exception as dns_error:
                        # Log DNS resolution failure
                        logger.error(f"DNS resolution failed for {host}: system DNS={e}, public DNS={dns_error}")
                    raise e
            
            # Override socket.getaddrinfo
            socket.getaddrinfo = custom_getaddrinfo
            
        except Exception as e:
            logger.error(f"Failed to configure custom DNS: {e}")
    
    def _setup_session_headers(self):
        """Setup realistic browser headers"""
        user_agent = self.ua.random
        
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        
        self.session.headers.update(headers)
    
    def bypass_cloudflare(self, url: str, method: str = 'GET', data: Optional[Dict] = None, 
                         headers: Optional[Dict] = None, cookies: Optional[Dict] = None) -> Optional[requests.Response]:
        """
        Main bypass method that tries multiple strategies
        
        Args:
            url: Target URL
            method: HTTP method (GET, POST, etc.)
            data: Form data for POST requests
            headers: Additional headers
            cookies: Session cookies
            
        Returns:
            Response object or None if all methods fail
        """
        
        # Build list of available bypass methods
        bypass_methods = [
            self._bypass_with_cloudscraper,
            self._bypass_with_advanced_requests,
            self._bypass_with_httpx,
        ]
        
        # Add optional methods if libraries are available
        if REQUESTS_HTML_AVAILABLE:
            bypass_methods.append(self._bypass_with_requests_html)
        
        if SELENIUM_AVAILABLE:
            bypass_methods.append(self._bypass_with_selenium)
        
        for i, bypass_method in enumerate(bypass_methods, 1):
            try:
                response = bypass_method(url, method, data, headers, cookies)
                
                if response and self._is_response_valid(response):
                    return response
                    
            except Exception as e:
                continue
        
        print("ERROR: Cloudflare bypass failed")
        return None
    
    def _bypass_with_cloudscraper(self, url: str, method: str = 'GET', data: Optional[Dict] = None,
                                 headers: Optional[Dict] = None, cookies: Optional[Dict] = None) -> Optional[requests.Response]:
        """Bypass using cloudscraper library"""
        try:
            if headers:
                self.cloudscraper_session.headers.update(headers)
            
            if cookies:
                self.cloudscraper_session.cookies.update(cookies)
            
            if method.upper() == 'POST':
                response = self.cloudscraper_session.post(url, data=data, timeout=30)
            else:
                response = self.cloudscraper_session.get(url, timeout=30)
            
            # IMPORTANT FIX: Copy session cookies to response object
            # Cloudscraper stores cookies in the session, not always in response
            # Use direct assignment to avoid "multiple cookies with same name" error
            for cookie_name, cookie_value in self.cloudscraper_session.cookies.items():
                response.cookies.set(cookie_name, cookie_value)
            
            return response
            
        except Exception as e:
            logger.error(f"Cloudscraper method failed: {e}")
            return None
    
    def _bypass_with_advanced_requests(self, url: str, method: str = 'GET', data: Optional[Dict] = None,
                                     headers: Optional[Dict] = None, cookies: Optional[Dict] = None) -> Optional[requests.Response]:
        """Bypass with advanced requests session"""
        try:
            # Randomize some headers
            self._randomize_headers()
            
            if headers:
                self.session.headers.update(headers)
            
            if cookies:
                self.session.cookies.update(cookies)
            
            # Add random delay
            time.sleep(random.uniform(1, 3))
            
            if method.upper() == 'POST':
                response = self.session.post(url, data=data, timeout=30, allow_redirects=True)
            else:
                response = self.session.get(url, timeout=30, allow_redirects=True)
            
            # Ensure response content is decoded properly
            # requests library should handle this automatically, but let's verify
            if response.encoding is None:
                response.encoding = response.apparent_encoding
            
            return response
            
        except Exception as e:
            logger.error(f"Advanced requests method failed: {e}")
            return None
    
    def _bypass_with_httpx(self, url: str, method: str = 'GET', data: Optional[Dict] = None,
                          headers: Optional[Dict] = None, cookies: Optional[Dict] = None) -> Optional[requests.Response]:
        """Bypass using httpx with HTTP/2 support"""
        try:
            client_headers = {
                'User-Agent': self.ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
            }
            
            if headers:
                client_headers.update(headers)
            
            # Try HTTP/2, fallback to HTTP/1.1 if h2 package not installed
            try:
                with httpx.Client(headers=client_headers, timeout=30.0, http2=True) as client:
                    if cookies:
                        client.cookies.update(cookies)
                    
                    if method.upper() == 'POST':
                        response = client.post(url, data=data)
                    else:
                        response = client.get(url)
                    
                    # Convert httpx response to requests-like response
                    requests_response = requests.Response()
                    requests_response.status_code = response.status_code
                    requests_response.headers = response.headers
                    requests_response._content = response.content
                    requests_response.url = str(response.url)
                    requests_response.cookies = response.cookies
                    
                    return requests_response
            except Exception as http2_error:
                # If HTTP/2 fails (h2 package missing), try HTTP/1.1
                if 'h2' in str(http2_error).lower():
                    with httpx.Client(headers=client_headers, timeout=30.0, http2=False) as client:
                        if cookies:
                            client.cookies.update(cookies)
                        
                        if method.upper() == 'POST':
                            response = client.post(url, data=data)
                        else:
                            response = client.get(url)
                        
                        # Convert httpx response to requests-like response
                        requests_response = requests.Response()
                        requests_response.status_code = response.status_code
                        requests_response.headers = response.headers
                        requests_response._content = response.content
                        requests_response.url = str(response.url)
                        requests_response.cookies = response.cookies
                        
                        return requests_response
                else:
                    raise
                
        except Exception as e:
            # Only log error if it's not about h2 package
            if 'h2' not in str(e).lower():
                logger.error(f"HTTPX method failed: {e}")
            return None
    
    def _bypass_with_requests_html(self, url: str, method: str = 'GET', data: Optional[Dict] = None,
                                  headers: Optional[Dict] = None, cookies: Optional[Dict] = None) -> Optional[requests.Response]:
        """Bypass using requests-html with JavaScript rendering"""
        if not REQUESTS_HTML_AVAILABLE:
            return None
            
        try:
            session = HTMLSession()
            
            if headers:
                session.headers.update(headers)
            
            if cookies:
                session.cookies.update(cookies)
            
            if method.upper() == 'POST':
                response = session.post(url, data=data)
            else:
                response = session.get(url)
            
            # Render JavaScript if needed
            try:
                response.html.render(timeout=20, keep_page=True)
                time.sleep(2)
            except Exception:
                pass
            
            return response
            
        except Exception as e:
            logger.error(f"Requests-HTML method failed: {e}")
            return None
    
    def _bypass_with_selenium(self, url: str, method: str = 'GET', data: Optional[Dict] = None,
                             headers: Optional[Dict] = None, cookies: Optional[Dict] = None) -> Optional[requests.Response]:
        """Bypass using undetected Chrome browser"""
        if not SELENIUM_AVAILABLE:
            return None
            
        driver = None
        try:
            # Setup undetected Chrome
            options = uc.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Add headless mode for server environments
            if getattr(self.config, 'selenium_headless', True):
                options.add_argument('--headless')
            
            driver = uc.Chrome(options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Set cookies if provided
            if cookies:
                driver.get(url)
                for name, value in cookies.items():
                    driver.add_cookie({'name': name, 'value': value})
            
            # Navigate to URL
            driver.get(url)
            
            # Wait for Cloudflare challenge to complete
            self._wait_for_cloudflare_bypass(driver)
            
            # Handle POST data if provided
            if method.upper() == 'POST' and data:
                self._handle_post_data(driver, data)
            
            # Get page content
            html_content = driver.page_source
            
            # Create a mock response object
            response = requests.Response()
            response.status_code = 200
            response._content = html_content.encode('utf-8')
            response.url = driver.current_url
            
            # Get cookies from browser
            browser_cookies = {}
            for cookie in driver.get_cookies():
                browser_cookies[cookie['name']] = cookie['value']
            
            response.cookies.update(browser_cookies)
            
            return response
            
        except Exception as e:
            logger.error(f"Selenium method failed: {e}")
            return None
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def _wait_for_cloudflare_bypass(self, driver, timeout: int = 30):
        """Wait for Cloudflare challenge to complete"""
        try:
            wait = WebDriverWait(driver, timeout)
            
            cloudflare_indicators = [
                "//div[contains(@class, 'cf-')]",
                "//div[contains(text(), 'Checking your browser')]",
                "//div[contains(text(), 'Please wait')]",
                "//div[contains(text(), 'DDoS protection')]",
                "//*[contains(text(), 'Cloudflare')]"
            ]
            
            for indicator in cloudflare_indicators:
                try:
                    element = driver.find_element(By.XPATH, indicator)
                    if element:
                        wait.until(EC.staleness_of(element))
                        break
                except:
                    continue
            
            time.sleep(random.uniform(2, 5))
            
        except TimeoutException:
            pass
        except Exception:
            pass
    
    def _handle_post_data(self, driver, data: Dict):
        """Handle POST data submission via Selenium"""
        try:
            # Look for a form to submit data
            forms = driver.find_elements(By.TAG_NAME, "form")
            
            if forms:
                form = forms[0]  # Use the first form found
                
                for field_name, field_value in data.items():
                    try:
                        # Try to find input field by name
                        input_field = driver.find_element(By.NAME, field_name)
                        input_field.clear()
                        input_field.send_keys(field_value)
                    except:
                        # Try to find by other attributes
                        try:
                            input_field = driver.find_element(By.CSS_SELECTOR, f"input[name*='{field_name}']")
                            input_field.clear()
                            input_field.send_keys(field_value)
                        except:
                            pass
                
                # Submit the form
                form.submit()
                time.sleep(3)  # Wait for submission
                
        except Exception as e:
            logger.error(f"Error handling POST data: {e}")
    
    def _randomize_headers(self):
        """Randomize some headers to appear more human"""
        self.session.headers['User-Agent'] = self.ua.random
        
        # Randomize accept-language
        languages = [
            'en-US,en;q=0.9',
            'en-GB,en;q=0.9',
            'en-US,en;q=0.8,es;q=0.7',
            'en-US,en;q=0.9,fr;q=0.8'
        ]
        self.session.headers['Accept-Language'] = random.choice(languages)
    
    def _is_response_valid(self, response) -> bool:
        """Check if response successfully bypassed Cloudflare"""
        if not response:
            return False
        
        if response.status_code != 200:
            return False
        
        content = response.text if hasattr(response, 'text') else response.content.decode('utf-8', errors='ignore')
        
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
        
        for indicator in challenge_indicators:
            if indicator in content:
                return False
        
        if '<title>' in content.lower():
            title_start = content.lower().find('<title>')
            title_end = content.lower().find('</title>', title_start)
            if title_start != -1 and title_end != -1:
                title = content[title_start:title_end].lower()
                if 'cloudflare' in title and ('checking' in title or 'please wait' in title or 'attention' in title):
                    return False
        
        if len(content.strip()) < 100:
            return False
        
        return True
    
    def get_session_cookies(self) -> Dict[str, str]:
        """Get current session cookies"""
        cookies = {}
        
        if self.session and self.session.cookies:
            for cookie in self.session.cookies:
                cookies[cookie.name] = cookie.value
        
        if self.cloudscraper_session and self.cloudscraper_session.cookies:
            for cookie in self.cloudscraper_session.cookies:
                cookies[cookie.name] = cookie.value
        
        return cookies
    
    def close(self):
        """Clean up resources"""
        if self.session:
            self.session.close()
        
        if self.cloudscraper_session:
            self.cloudscraper_session.close()
        
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

# Global instance will be created in http_service
