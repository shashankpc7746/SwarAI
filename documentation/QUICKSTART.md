```markdown
# SwarAI Quick Start Guide

## 🚀 Quick Start (Windows)

Simply double-click `start-swarai.bat` to start both backend and frontend servers!

The script will:
1. Install required Python packages (PyJWT, python-jose, passlib)
2. Start the backend server (http://localhost:8000)
3. Install Node.js packages (if needed)
4. Start the frontend server (http://localhost:3000)
5. Open the login page in your browser

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

1. The login page will show with "Welcome to Swar AI" animation
2. Fill in your details:
   - **Name**: Your full name
   - **Gmail**: Your email address
   - **Age**: Your age (13-120)
3. Click "Sign In"
4. You're in! Start using Swar AI Voice Assistant

## 🔑 Authentication Flow

```
Browser → Login Page → Enter Details → Backend Authentication
   ↓
JWT Token Generated
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
- ✅ And more!

## 🔄 Logout

Click the logout icon in the top-right corner to log out.

## 💡 Tips

- Your session persists for 7 days
- You can close and reopen the browser without logging in again
- Use the logout button to end your session securely

## 📚 More Information

See `AUTHENTICATION_GUIDE.md` for detailed documentation.

---

**Enjoy using SwarAI! 🎉**

```
