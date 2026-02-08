"""
Authentication Models and Schemas
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class User(BaseModel):
    """User model"""
    id: str
    name: str
    email: EmailStr
    age: int
    profilePicture: Optional[str] = None
    createdAt: datetime

class UserCreate(BaseModel):
    """User creation schema"""
    name: str
    email: EmailStr
    age: int

class UserLogin(BaseModel):
    """User login schema"""
    name: str
    email: EmailStr
    age: int

class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"

class AuthResponse(BaseModel):
    """Authentication response schema"""
    user: User
    token: str
