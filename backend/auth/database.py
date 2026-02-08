"""
Authentication Database
Simple in-memory database for users (for development)
In production, use a real database like PostgreSQL, MongoDB, etc.
"""

from typing import Dict, Optional
from auth.models import User
from datetime import datetime

class AuthDatabase:
    """Simple in-memory user database"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
    
    def create_user(self, user: User) -> User:
        """Create a new user"""
        self.users[user.id] = user
        return user
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        for user in self.users.values():
            if user.email == email:
                return user
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def update_user(self, user_id: str, update_data: dict) -> Optional[User]:
        """Update user information"""
        user = self.users.get(user_id)
        if user:
            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            return user
        return None
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user"""
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False

# Global database instance
auth_db = AuthDatabase()
