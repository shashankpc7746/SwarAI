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

@router.post("/google")
async def google_login(token: dict):
    """
    Google OAuth login endpoint
    Receives Google ID token from frontend and validates it
    Only accesses name and email from Google account
    """
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests
        import os
        
        logger.info("🔐 Google OAuth login attempt started")
        
        google_token = token.get('credential')
        if not google_token:
            logger.error("❌ No credential provided in request")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google token is required"
            )
        
        # Get Google Client ID from environment
        client_id = os.getenv('GOOGLE_CLIENT_ID') or os.getenv('NEXT_PUBLIC_GOOGLE_CLIENT_ID')
        
        if not client_id:
            logger.error("❌ GOOGLE_CLIENT_ID not found in environment variables")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server configuration error: Google Client ID not set"
            )
        
        logger.info(f"🔑 Using Client ID: {client_id[:20]}...")
        
        try:
            # Verify token with Google (this validates the token and returns user info)
            idinfo = id_token.verify_oauth2_token(
                google_token, 
                requests.Request(), 
                client_id
            )
            
            logger.info(f"✅ Token verified successfully. User info: {list(idinfo.keys())}")
            
            # Extract ONLY name and email from token (as requested)
            email = idinfo.get('email')
            name = idinfo.get('name')
            picture = idinfo.get('picture')  # Optional: for profile picture
            
            logger.info(f"📧 Email: {email}, 👤 Name: {name}")
            
            if not email:
                logger.error("❌ Email not found in Google token")
                raise ValueError("Email not found in token")
            
            if not name:
                logger.error("❌ Name not found in Google token")
                raise ValueError("Name not found in token")
            
            # Check if user exists
            existing_user = auth_db.get_user_by_email(email)

            if existing_user:
                logger.info(f"👤 Existing user found: {existing_user.id}")
                # Update profile picture if available
                if picture and existing_user.profilePicture != picture:
                    auth_db.update_user(existing_user.id, {
                        "profilePicture": picture
                    })
                    existing_user = auth_db.get_user_by_id(existing_user.id)
                user = existing_user
            else:
                # Create new user from Google account (name and email only)
                logger.info(f"🆕 Creating new user for: {email}")
                user_id = generate_user_id()
                user = User(
                    id=user_id,
                    name=name,
                    email=email,
                    age=18,  # Default age for Google OAuth users
                    profilePicture=picture if picture else None,
                    createdAt=datetime.now(timezone.utc)
                )
                auth_db.create_user(user)
                logger.info(f"✅ New user created: {user.id}")
            
            # Generate JWT token
            access_token = create_access_token(
                data={"sub": user.id, "email": user.email}
            )
            
            logger.info(f"✅ User logged in via Google: {user.email}")
            
            return AuthResponse(
                user=user,
                token=access_token
            )
            
        except ValueError as e:
            error_msg = str(e)
            logger.error(f"❌ Token validation error: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid Google token: {error_msg}"
            )
    
    except ImportError as e:
        logger.error(f"❌ google-auth library not installed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth requires google-auth library. Install: pip install google-auth"
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"❌ Google login error: {str(e)}")
        logger.error(f"Traceback: {error_trace}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google login failed: {str(e)}"
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
