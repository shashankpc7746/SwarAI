"""
Authentication Routes
Login, Logout, and Google OAuth endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import RedirectResponse
from auth.models import UserLogin, AuthResponse, User
from auth.utils import create_access_token, verify_token, generate_user_id
from auth.database import auth_db
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/login", response_model=AuthResponse)
async def login(credentials: UserLogin):
    """
    Login endpoint - Create or authenticate user
    """
    try:
        # Check if user exists
        existing_user = auth_db.get_user_by_email(credentials.email)
        
        if existing_user:
            # User exists, update info if needed
            if existing_user.name != credentials.name or existing_user.age != credentials.age:
                auth_db.update_user(existing_user.id, {
                    "name": credentials.name,
                    "age": credentials.age
                })
                existing_user = auth_db.get_user_by_id(existing_user.id)
            
            user = existing_user
        else:
            # Create new user
            user_id = generate_user_id()
            user = User(
                id=user_id,
                name=credentials.name,
                email=credentials.email,
                age=credentials.age,
                createdAt=datetime.now(timezone.utc)
            )
            auth_db.create_user(user)
        
        # Generate JWT token
        access_token = create_access_token(
            data={"sub": user.id, "email": user.email}
        )
        
        logger.info(f"✅ User logged in: {user.email}")
        
        return AuthResponse(
            user=user,
            token=access_token
        )
    
    except Exception as e:
        logger.error(f"❌ Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.get("/google")
async def google_login():
    """
    Google OAuth login endpoint
    Redirects to Google OAuth consent screen
    """
    # In a production environment, you would:
    # 1. Redirect to Google OAuth URL with client_id, redirect_uri, etc.
    # 2. Handle the callback in /api/auth/google/callback
    # 3. Exchange authorization code for access token
    # 4. Get user info from Google
    # 5. Create/update user in database
    # 6. Generate JWT token
    # 7. Redirect to frontend with token
    
    # For now, return a simple message
    # You'll need to set up Google OAuth credentials and implement the full flow
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Google OAuth not yet implemented. Please use regular login."
    )

@router.get("/google/callback")
async def google_callback(code: str):
    """
    Google OAuth callback endpoint
    Handles the redirect from Google after user authorization
    """
    # This would handle the OAuth callback from Google
    # Exchange code for token, get user info, create/login user
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Google OAuth callback not yet implemented"
    )

@router.post("/logout")
async def logout():
    """
    Logout endpoint
    In a stateless JWT system, logout is handled client-side by removing the token
    """
    return {"message": "Logged out successfully"}

@router.get("/verify")
async def verify_user(token: str):
    """
    Verify JWT token and return user info
    """
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = payload.get("sub")
    user = auth_db.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"user": user}
