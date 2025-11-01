"""
Login controller - handles authentication API endpoints
"""
from flask import Blueprint, request
import logging
from app.config.config import config
from app.services.http_service import http_service
from app.services.login_service import LoginService
from app.utils.response_utils import create_success_response, create_error_response
from app.models.dto import LoginRequest, LoginResponse

logger = logging.getLogger(__name__)

login_bp = Blueprint('login', __name__)


@login_bp.route('/api/login', methods=['POST'])
def login():
    """
    Login endpoint - authenticate user and return session token
    """
    try:
        # Step 1: Parse and validate request
        data = request.get_json()
        if not data:
            return create_error_response("Invalid request data", status_code=400)
        
        login_req = LoginRequest.from_dict(data)
        
        # Step 2: Validate credentials
        is_valid, error_msg = LoginService.validate_credentials(
            login_req.username, 
            login_req.password
        )
        if not is_valid:
            return create_error_response(error_msg, "INVALID_CREDENTIALS", status_code=401)
        
        # Step 3: Prepare login data
        login_data = LoginService.prepare_login_data(
            login_req.username,
            login_req.password
        )
        
        # Step 4: Make login request
        login_url = f"{config.base_url}/user/login"
        response = http_service.post(login_url, data=login_data)
        
        # Step 5: Check if login was successful
        if not LoginService.check_login_success(response.text):
            return create_error_response(
                "Invalid username or password",
                "LOGIN_FAILED",
                status_code=401
            )
        
        # Step 6: Extract session cookie
        session_cookie = LoginService.extract_session_cookie(response)
        if not session_cookie:
            return create_error_response(
                "Login failed - no session cookie",
                "NO_SESSION_COOKIE",
                status_code=401
            )
        
        # Step 7: Log successful login and return response
        print(f"User: {login_req.username} logged in")
        login_response = LoginResponse("Login successful", session_cookie)
        return create_success_response(login_response.to_dict())
        
    except Exception as e:
        logger.error(f"Error during login: {e}", exc_info=True)
        return create_error_response(
            f"Login error: {str(e)}",
            "SERVER_ERROR",
            status_code=500
        )
