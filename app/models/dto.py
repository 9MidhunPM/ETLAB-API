from dataclasses import dataclass, field
from typing import Optional, Any
from datetime import datetime
import json

@dataclass
class LoginRequest:
    username: str = ""
    password: str = ""
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            username=data.get('username', ''),
            password=data.get('password', '')
        )

@dataclass
class LoginResponse:
    message: str = ""
    token: str = ""
    
    def to_dict(self) -> dict:
        return {
            'message': self.message,
            'token': self.token
        }

@dataclass
class ApiResponse:
    message: str = ""
    data: Optional[Any] = None
    status: Optional[str] = None
    
    def __init__(self, message: str, data: Optional[Any] = None, status: Optional[str] = None):
        self.message = message
        self.data = data
        self.status = status
    
    def to_dict(self) -> dict:
        result = {'message': self.message}
        if self.data is not None:
            result['data'] = self.data
        if self.status is not None:
            result['status'] = self.status
        return result