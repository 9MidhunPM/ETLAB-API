"""
Response formatting utilities
"""
from typing import Any, Dict, Optional
from flask import jsonify


def create_success_response(data: Any, message: Optional[str] = None, status_code: int = 200):
    """
    Create a standardized success response
    
    Args:
        data: Response data
        message: Optional success message
        status_code: HTTP status code (default: 200)
    
    Returns:
        Flask JSON response tuple (response, status_code)
    """
    response = {
        "success": True,
        "data": data
    }
    
    if message:
        response["message"] = message
    
    return jsonify(response), status_code


def create_error_response(message: str, error_code: Optional[str] = None, 
                         details: Optional[Dict] = None, status_code: int = 400):
    """
    Create a standardized error response
    
    Args:
        message: Error message
        error_code: Optional error code for client handling
        details: Optional additional error details
        status_code: HTTP status code (default: 400)
    
    Returns:
        Flask JSON response tuple (response, status_code)
    """
    response = {
        "success": False,
        "error": message
    }
    
    if error_code:
        response["error_code"] = error_code
    
    if details:
        response["details"] = details
    
    return jsonify(response), status_code


def create_unauthorized_response(message: str = "Authorization token is required"):
    """
    Create a 401 Unauthorized response
    
    Args:
        message: Error message
    
    Returns:
        Flask JSON response tuple (response, 401)
    """
    return create_error_response(message, "UNAUTHORIZED", status_code=401)


def create_token_expired_response(message: str = "Token expired. Please login again."):
    """
    Create a 401 Token Expired response
    
    Args:
        message: Error message
    
    Returns:
        Flask JSON response tuple (response, 401)
    """
    return create_error_response(message, "TOKEN_EXPIRED", status_code=401)
