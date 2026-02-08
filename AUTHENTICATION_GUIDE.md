# SwarAI Authentication System

## 🎉 Overview

The SwarAI application now includes a complete authentication system with:

- **Modern Login Page** with beautiful intro animation
- **User Registration** with Name, Email (Gmail), and Age
- **JWT-based Authentication** for secure sessions
- **Google Sign-In Integration** (frontend ready, backend placeholder)
- **Protected Routes** - Main app only accessible after login
- **User Profile Display** with logout functionality
- **Persistent Sessions** using localStorage

## 🌟 Features

### Login Page
- **Intro Animation**: "Welcome to Swar AI" with sparkles and floating particles
- **Modern Black-White Theme**: Glassmorphic design with backdrop blur
- **Form Validation**: Real-time validation for all fields
- **Smooth Transitions**: Framer Motion animations throughout
- **Thank You Message**: Appears after successful login

### Security
- **JWT Tokens**: Secure token-based authentication
- **Token Expiration**: 7-day token validity (configurable)
- **Protected Routes**: Automatic redirect to login if not authenticated
- **Session Persistence**: Login state preserved across browser sessions

### User Experience
- **Loading States**: Smooth loading indicators
- **Error Handling**: Clear error messages for validation
- **Logout Button**: Easy logout from header
- **User Profile Display**: Shows user info in header

## 📁 File Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── login/
│   │   │   └── page.tsx              # Login route
│   │   ├── auth/
│   │   │   └── callback/
│   │   │       └── page.tsx          # OAuth callback handler
│   │   ├── page.tsx                  # Main app (protected)
│   │   └── layout.tsx                # Root layout with AuthProvider
│   ├── components/
│   │   ├── LoginPage.tsx             # Login page component
│   │   ├── ProtectedRoute.tsx        # Route protection wrapper
│   │   └── LogoutHeader.tsx          # Header with user info & logout
│   ├── context/
│   │   └── AuthContext.tsx           # Authentication context & hooks
│   └── types/
│       └── auth.ts                    # TypeScript types for auth

backend/
├── auth/
│   ├── __init__.py                    # Module exports
│   ├── models.py                      # User & auth models
│   ├── routes.py                      # Authentication endpoints
│   ├── utils.py                       # JWT utilities
│   └── database.py                    # In-memory user database
└── main.py                            # Updated with auth routes
```

## 🚀 Setup Instructions

### Backend Setup

1. **Install Required Packages**

```bash
cd backend
pip install PyJWT==2.8.0 python-jose[cryptography]>=3.3.0 passlib[bcrypt]>=1.7.4
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

2. **Start the Backend Server**

```bash
python main.py
```

The backend will run on `http://localhost:8000`

### Frontend Setup

1. **Install Dependencies** (if not already done)

```bash
cd frontend
npm install
```

2. **Start the Development Server**

```bash
npm run dev
```

The frontend will run on `http://localhost:3000`

## 🎯 How to Use

### First Time Setup

1. Navigate to `http://localhost:3000`
2. You'll see the login page with "Welcome to Swar AI" animation (3 seconds)
3. The login form will fade in

### Logging In

1. Fill in the form:
   - **Name**: Your full name (minimum 2 characters)
   - **Gmail**: Your email address (must be valid format)
   - **Age**: Your age (13-120)

2. Click **"Sign In"** button

3. You'll see a "Thank You!" message

4. The main SwarAI Voice Assistant page will load

### Using the App

- Your user information appears in the top-right corner
- Click the logout icon to log out
- After logout, you'll be redirected to the login page

### Session Persistence

- Your login session persists across browser refreshes
- Tokens are valid for 7 days
- After expiration, you'll need to log in again

## 🔧 API Endpoints

### POST `/api/auth/login`

Login or create a new user.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@gmail.com",
  "age": 25
}
```

**Response:**
```json
{
  "user": {
    "id": "user_abc123",
    "name": "John Doe",
    "email": "john@gmail.com",
    "age": 25,
    "createdAt": "2026-02-08T12:00:00"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### GET `/api/auth/google`

Initiates Google OAuth flow (placeholder - returns 501).

### POST `/api/auth/logout`

Logout endpoint (client-side token removal).

### GET `/api/auth/verify?token=<token>`

Verify JWT token and get user info.

## 🎨 Customization

### Change Token Expiration

Edit `backend/auth/utils.py`:

```python
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
```

### Customize Login Page Theme

Edit `frontend/src/components/LoginPage.tsx`:

- Change colors in the gradient backgrounds
- Modify animation durations
- Adjust form styling

### Add More User Fields

1. Update `backend/auth/models.py`:
```python
class User(BaseModel):
    # ... existing fields
    phone: Optional[str] = None  # Add new field
```

2. Update `frontend/src/types/auth.ts`:
```typescript
export interface User {
  // ... existing fields
  phone?: string;  // Add new field
}
```

3. Update login form in `LoginPage.tsx`

## 🔐 Security Notes

### Current Implementation (Development)

- **In-Memory Database**: Users stored in memory (lost on restart)
- **Simple Secret Key**: Generated on startup
- **No Password Hashing**: Current version uses email-based login

### Production Recommendations

1. **Use Real Database**:
   - PostgreSQL, MongoDB, or similar
   - Persistent user storage

2. **Environment Variables**:
   ```bash
   # .env file
   JWT_SECRET_KEY=your-super-secret-key-here
   DATABASE_URL=postgresql://...
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   ```

3. **HTTPS Only**:
   - Use HTTPS in production
   - Secure cookie flags

4. **Rate Limiting**:
   - Add rate limiting to prevent brute force
   - Use libraries like `slowapi`

5. **Password Hashing**:
   - If adding password authentication, use bcrypt
   - Never store plain text passwords

## 🌐 Google OAuth Integration

The frontend is ready for Google OAuth. To complete the integration:

1. **Get Google OAuth Credentials**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or use existing
   - Enable Google+ API
   - Create OAuth 2.0 credentials
   - Add authorized redirect URI: `http://localhost:8000/api/auth/google/callback`

2. **Update Backend** (`backend/auth/routes.py`):

```python
import httpx
from urllib.parse import urlencode

GOOGLE_CLIENT_ID = "your-client-id"
GOOGLE_CLIENT_SECRET = "your-client-secret"
REDIRECT_URI = "http://localhost:8000/api/auth/google/callback"

@router.get("/google")
async def google_login():
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline"
    }
    google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return RedirectResponse(google_auth_url)

@router.get("/google/callback")
async def google_callback(code: str):
    # Exchange code for tokens
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data)
        tokens = response.json()
        
        # Get user info
        user_info_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        user_info = user_info_response.json()
    
    # Create or update user in database
    # Generate JWT token
    # Redirect to frontend with token
    
    return RedirectResponse(f"http://localhost:3000/auth/callback?token={jwt_token}")
```

## 🐛 Troubleshooting

### "Login failed" Error

- Check backend is running on port 8000
- Check browser console for network errors
- Verify CORS settings in `main.py`

### Stuck on Loading Screen

- Clear localStorage: `localStorage.clear()`
- Check for JavaScript errors in console
- Verify backend authentication endpoints are working

### Token Expired

- Login again to get a new token
- Tokens expire after 7 days by default

### Google Sign-In Not Working

- Currently returns 501 (Not Implemented)
- Follow Google OAuth integration steps above

## 📝 Development Notes

### Testing Authentication

```javascript
// In browser console

// Check current auth state
localStorage.getItem('swarai_user')
localStorage.getItem('swarai_token')

// Clear auth (logout)
localStorage.clear()
window.location.reload()
```

### Backend Testing

```bash
# Test login endpoint
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@gmail.com", "age": 25}'

# Test verify endpoint
curl "http://localhost:8000/api/auth/verify?token=YOUR_TOKEN_HERE"
```

## 🎉 What's Next?

- ✅ Basic authentication working
- ⏳ Complete Google OAuth integration
- ⏳ Add password-based authentication option
- ⏳ Implement real database (PostgreSQL/MongoDB)
- ⏳ Add "Remember Me" functionality
- ⏳ Email verification
- ⏳ Password reset flow
- ⏳ Two-factor authentication (2FA)
- ⏳ User profile editing
- ⏳ Social login (GitHub, Facebook, etc.)

## 📚 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Authentication](https://nextjs.org/docs/authentication)
- [JWT.io](https://jwt.io/) - JWT debugger
- [Google OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)

---

**Created with ❤️ for SwarAI**
