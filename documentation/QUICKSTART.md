```markdown
# SwarAI Quick Start Guide

## 🚀 Quick Start (Windows)

Simply double-click `start-swarai.bat` to start both backend and frontend servers!

The script will:
1. Install required Python packages (google-auth, PyJWT, python-jose, passlib)
2. Start the backend server (http://localhost:8000)
3. Install Node.js packages (if needed)
4. Start the frontend server (http://localhost:3000)
5. Open the login page in your browser

## ⚙️ First-Time Setup

Before running SwarAI for the first time, configure your environment variables:

### 1. Backend Configuration

Edit `backend/.env`:

```env
# Required: Get from https://console.groq.com/
GROQ_API_KEY=your_groq_api_key_here

# Required: Get from https://console.cloud.google.com/apis/credentials
GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
```

### 2. Frontend Configuration

Create `frontend/.env.local`:

```env
# Required: Same Google Client ID as backend
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com

# Required: Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Get Google OAuth Client ID

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create OAuth 2.0 Client ID
3. Add authorized origins: `http://localhost:3000`
4. Add redirect URIs: `http://localhost:3000/auth/callback`
5. Copy your Client ID

📚 **Detailed guide**: See `documentation/backend/AUTHENTICATION_GUIDE.md`

## 📋 Manual Start

### Option 1: Backend First

1. **Start Backend**:
```bash
cd backend
python main.py
```

2. **Start Frontend** (in a new terminal):
```bash
cd frontend
npm run dev
```

3. **Open Browser**:
Navigate to http://localhost:3000

### Option 2: PowerShell

```powershell
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

## 🎯 First Time Login

You have two options to log in:

### Option A: Sign in with Google (Recommended)

1. Click the **"Sign in with Google"** button
2. Select your Google account in the popup
3. Grant permissions
4. You're in! Start using SwarAI

### Option B: Manual Login

1. Fill in your details:
   - **Name**: Your full name
   - **Gmail**: Your email address
   - **Age**: Your age (13-120)
2. Click "Sign In"
3. You're in! Start using SwarAI

## 🔑 Authentication Flow

```
Browser → Login Page → Choose Login Method
   ↓
Manual Login OR Google OAuth
   ↓
JWT Token Generated (7-day expiry)
   ↓
Token Stored in LocalStorage
   ↓
Main Page Loads → Protected Content Accessible
```

## 📱 Features Available

After login, you can:
- ✅ Use voice commands
- ✅ Chat with AI agents
- ✅ Search files
- ✅ Send WhatsApp messages
- ✅ Draft emails
- ✅ Manage tasks
- ✅ Control system (volume, brightness, etc.)
- ✅ Launch applications
- ✅ And more!

## 🔄 Logout

Click your profile icon in the top-right corner, then click **Logout** to end your session.

## 💡 Tips

- Your session persists for **7 days**
- You can close and reopen the browser without logging in again
- Google OAuth is the fastest way to log in
- Your profile picture from Google will be displayed (if using Google login)
- Use the logout button to end your session securely

## 🐛 Troubleshooting

### "Missing required parameter: client_id"
- Make sure you created `frontend/.env.local` with `NEXT_PUBLIC_GOOGLE_CLIENT_ID`
- Restart the frontend server after creating the file

### "Google OAuth requires google-auth library"
- Run: `pip install google-auth google-auth-oauthlib google-auth-httplib2`
- Restart the backend server

### Backend Not Starting
- Verify `GROQ_API_KEY` is set in `backend/.env`
- Check Python version (requires 3.10+)
- Activate virtual environment: `venv\Scripts\activate`

### Frontend Not Building
- Run: `npm install --legacy-peer-deps`
- Delete `node_modules` and `.next` folders, then reinstall

## 📚 More Information

- **Authentication Guide**: `documentation/backend/AUTHENTICATION_GUIDE.md`
- **Full README**: `README.md`
- **Backend Fixes**: `documentation/backend/BACKEND_FIXES.md`

---

**Enjoy using SwarAI! 🎉**

```
