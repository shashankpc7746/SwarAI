```markdown
# SwarAI Authentication System

## 🎉 Overview

The SwarAI application includes a complete authentication system with:

- **Modern Login Page** with beautiful intro animation
- **User Registration** with Name, Email, and Age
- **Google OAuth 2.0 Integration** - Sign in with Google account
- **JWT-based Authentication** for secure sessions
- **Protected Routes** - Main app only accessible after login
- **User Profile Display** with logout functionality
- **Persistent Sessions** using localStorage (7-day expiry)
- **In-Memory User Database** (no MongoDB required for auth)

---

## 🔐 Authentication Flow

### 1. **Manual Login (Name + Email + Age)**

```
User fills form → POST /api/auth/login → Backend validates
   ↓
JWT Token Generated (7-day expiry)
   ↓
Token + User Data stored in localStorage
   ↓
Redirect to Main Page
```

### 2. **Google OAuth Login**

```
User clicks "Sign in with Google" → Google OAuth popup
   ↓
Google returns credential token
   ↓
Frontend sends token to POST /api/auth/google
   ↓
Backend verifies token with Google API
   ↓
Extract name & email from verified token
   ↓
Create/Update user in database
   ↓
Generate JWT token
   ↓
Token + User Data stored in localStorage
   ↓
Redirect to Main Page
```

---

## 🔧 Google OAuth Setup

### Step 1: Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Google+ API** (or **Google Identity** API)
4. Navigate to **APIs & Services > Credentials**
5. Click **Create Credentials > OAuth 2.0 Client ID**
6. Configure OAuth consent screen if prompted:
   - User Type: External
   - App name: SwarAI
   - User support email: your email
   - Developer contact: your email
7. Application type: **Web application**
8. Add Authorized JavaScript origins:
   ```
   http://localhost:3000
   http://127.0.0.1:3000
   ```
9. Add Authorized redirect URIs:
   ```
   http://localhost:3000/auth/callback
   http://127.0.0.1:3000/auth/callback
   ```
10. Click **Create**
11. Copy your **Client ID** (format: `xxxx.apps.googleusercontent.com`)

### Step 2: Configure Backend

Edit `backend/.env`:

```env
# Google OAuth Configuration
GOOGLE_CLIENT_ID=1029594596579-fmnju53fveb24fjl45kculli6g5i5tnf.apps.googleusercontent.com
```

### Step 3: Configure Frontend

Create `frontend/.env.local`:

```env
# Google OAuth Configuration
NEXT_PUBLIC_GOOGLE_CLIENT_ID=1029594596579-fmnju53fveb24fjl45kculli6g5i5tnf.apps.googleusercontent.com

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Step 4: Install Backend Dependencies

```bash
cd backend
pip install google-auth google-auth-oauthlib google-auth-httplib2
```

These are already in `requirements.txt` but verify installation:

```bash
python -c "import google.oauth2.id_token; print('✅ Google Auth installed')"
```

### Step 5: Restart Servers

```bash
# Backend (press Ctrl+C, then restart)
python main.py

# Frontend (in another terminal, press Ctrl+C, then restart
cd frontend
npm run dev
```

---

## 🧪 Testing Authentication

### Test Manual Login

1. Go to http://localhost:3000/login
2. Fill in:
   - Name: Test User
   - Gmail: test@gmail.com
   - Age: 25
3. Click "Sign In"
4. Should redirect to main page

### Test Google OAuth

1. Go to http://localhost:3000/login
2. Click "Sign in with Google" button
3. Select your Google account in popup
4. Should redirect to main page
5. Check browser console for logs:
   ```
   🔐 Starting Google login process...
   📝 Credential received: Yes
   📡 Sending request to backend...
   📡 Backend response status: 200
   ✅ Login successful! User: [name] [email]
   ```

### Verify Protected Route

1. Logout (click profile icon > logout)
2. Try accessing http://localhost:3000 directly
3. Should redirect to /login
4. Login again - should access main page

---

## 🔑 JWT Token Structure

```json
{
  "sub": "user_abc123",
  "email": "user@gmail.com",
  "exp": 1234567890
}
```

- **sub**: User ID (unique identifier)
- **email**: User's email address
- **exp**: Token expiration (Unix timestamp)

Token is signed with `SECRET_KEY` from environment (defaults to random key if not set).

---

## 📦 User Data Structure

```json
{
  "id": "user_abc123",
  "name": "John Doe",
  "email": "john@gmail.com",
  "age": 25,
  "profilePicture": "https://lh3.googleusercontent.com/...",
  "createdAt": "2026-02-12T10:30:00Z"
}
```

Stored in:
- **Backend**: In-memory dictionary (`auth_db`)
- **Frontend**: localStorage as `swarai_user` (JSON string)

---

## 🔒 Security Features

1. **JWT Tokens** with 7-day expiration
2. **HTTPS-ready** (works with http in dev, https in production)
3. **Protected Routes** - ProtectedRoute component checks auth status
4. **Token Verification** - Backend verifies Google tokens with Google API
5. **Input Validation** - Age 13-120, valid email format
6. **CORS Configuration** - Only allows localhost:3000 in development

---

## 🐛 Troubleshooting

### Google OAuth Error: "Missing required parameter: client_id"

**Cause**: `NEXT_PUBLIC_GOOGLE_CLIENT_ID` not set in `frontend/.env.local`

**Fix**:
```bash
cd frontend
echo "NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com" > .env.local
# Restart frontend server
```

### Backend Error: "Google OAuth requires google-auth library"

**Cause**: `google-auth` not installed in backend virtual environment

**Fix**:
```bash
cd backend
pip install google-auth google-auth-oauthlib google-auth-httplib2
# Restart backend server
```

### Error: "Invalid Google token"

**Causes**:
1. Client ID mismatch between frontend and backend
2. Client ID not authorized in Google Console
3. Token expired

**Fix**:
1. Verify both frontend and backend have the same `GOOGLE_CLIENT_ID`
2. Check Google Console authorized origins/redirects
3. Try logging in again (tokens expire after ~1 hour)

### Frontend Not Receiving Token

**Cause**: CORS issues or backend not running

**Fix**:
1. Check backend is running on http://localhost:8000
2. Verify `NEXT_PUBLIC_API_URL` in `frontend/.env.local`
3. Check browser console for network errors

---

## 🚀 Production Deployment

### Additional Security for Production

1. **Use Environment Secrets Manager**:
   - DO NOT commit `.env` files to git
   - Use Vercel Secrets, AWS Secrets Manager, etc.

2. **Update Authorized Origins/Redirects**:
   ```
   https://yourdomain.com
   https://yourdomain.com/auth/callback
   ```

3. **Enable HTTPS Only**:
   - Update `frontend/.env.production`:
     ```env
     NEXT_PUBLIC_API_URL=https://api.yourdomain.com
     NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_production_client_id
     ```

4. **Set Strong SECRET_KEY in backend**:
   ```env
   SECRET_KEY=your_very_long_random_secret_key_here
   ```

5. **Consider MongoDB for User Persistence**:
   - In-memory database is lost on restart
   - Add MongoDB URL to store users permanently

---

## 📚 API Endpoints

### `POST /api/auth/login`

Manual login with email, name, age.

**Request**:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "age": 25
}
```

**Response**:
```json
{
  "user": { ...user object... },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6..."
}
```

### `POST /api/auth/google`

Google OAuth login.

**Request**:
```json
{
  "credential": "eyJhbGciOiJSUzI1NiIsImtpZCI6..."
}
```

**Response**:
```json
{
  "user": { ...user object... },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6..."
}
```

### `POST /api/auth/logout`

Logout endpoint (client-side token removal).

**Response**:
```json
{
  "message": "Logged out successfully"
}
```

### `GET /api/auth/verify?token=<jwt_token>`

Verify JWT token and return user info.

**Response**:
```json
{
  "user": { ...user object... }
}
```

---

## 🎨 UI Components

### LoginPage (`frontend/src/components/LoginPage.tsx`)

- Animated intro with SwarAI logo
- Manual login form (name, email, age)
- Google OAuth button (`@react-oauth/google`)
- Form validation
- Error handling with visual feedback

### ProtectedRoute (`frontend/src/components/ProtectedRoute.tsx`)

- Wraps main application
- Checks localStorage for token
- Redirects to /login if not authenticated
- Shows loading state during authentication check

### AuthContext (`frontend/src/context/AuthContext.tsx`)

- Global authentication state management
- `login()` - Manual login
- `loginWithGoogle()` - Google OAuth login
- `logout()` - Clear session
- `user` - Current user object
- `isAuthenticated` - Boolean auth status

---

**Last Updated**: February 12, 2026

```
