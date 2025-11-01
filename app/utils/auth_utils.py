"""
Authentication utilities
"""
from typing import Optional


def extract_token(auth_header: Optional[str]) -> Optional[str]:
    """
    Extract token from Authorization header
    
    Args:
        auth_header: Authorization header value (e.g., "Bearer <token>")
    
    Returns:
        Token string or None
    """
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header[7:]
    return None


def validate_token(token: Optional[str]) -> bool:
    """
    Validate if token exists and has minimum requirements
    
    Args:
        token: Token string to validate
    
    Returns:
        True if valid, False otherwise
    """
    return token is not None and len(token) > 0
