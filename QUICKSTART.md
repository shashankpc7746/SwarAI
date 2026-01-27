# 🚀 Vaani Quick Start Guide

## Get Started in 5 Minutes!

### Step 1: Start the Backend (2 minutes)

```powershell
# Navigate to backend
cd backend

# Install dependencies (first time only)
pip install -r requirements.txt

# Run the server
python main.py
```

✅ Backend running at: `http://localhost:8000`

---

### Step 2: Start the Frontend (2 minutes)

```powershell
# Open new terminal
cd frontend

# Install dependencies (first time only)
npm install

# Run the frontend
npm run dev
```

✅ Frontend running at: `http://localhost:3000`

---

### Step 3: Try Your First Commands! (1 minute)

Open your browser to `http://localhost:3000` and try:

#### 📱 Send WhatsApp Message
```
"Send WhatsApp to vijay: Hey, how are you?"
```

#### 📁 Find a File
```
"Find ownership document"
```

#### 📧 Send Email
```
"Email boss about project update"
```

#### 📞 Make a Call
```
"Call mom"
```

#### 💰 Send Payment
```
"Pay $50 to john via PayPal"
```

#### 🌐 Search Web
```
"Google python tutorials"
```

#### 📅 Schedule Meeting
```
"Schedule meeting tomorrow at 3pm"
```

#### ✅ Add Task
```
"Add task buy groceries"
```

#### 🚀 Open Application
```
"Open Chrome"
```

---

## 🎯 What Happens?

1. **Voice/Text Input** → You speak or type
2. **AI Processing** → Groq AI understands intent
3. **Agent Routing** → Correct agent handles task
4. **Action Execution** → App opens with pre-filled data
5. **You Click Send** → One click to complete!

---

## 📋 Customization

### Add Your Contacts

Edit `backend/agents/whatsapp_agent.py` and `phone_agent.py`:

```python
mock_contacts = {
    "vijay": "+919876543211",
    "mom": "+919876543212",
    "your_friend": "+91xxxxxxxxxx",  # Add here
}
```

### Set Your Email

Edit `backend/.env`:

```env
DEFAULT_EMAIL_FROM=your-email@gmail.com
```

### Configure File Search

Edit `backend/.env`:

```env
SEARCH_DIRECTORIES=C:\Users\YourName\Documents,C:\Downloads
```

---

## 🎤 Voice Commands

Click the 🎤 button and speak naturally:

- "Send WhatsApp to [name]: [message]"
- "Find [filename]"
- "Email [person] about [topic]"
- "Call [name]"
- "Pay [amount] to [person] via [app]"
- "Open [application]"
- "Google [search query]"
- "Schedule meeting [when]"
- "Add task [task name]"

---

## ⚡ Pro Tips

1. **Be Natural**: Speak like you're talking to a person
2. **Be Specific**: Include names, amounts, times
3. **Chain Commands**: "Find report and send to boss on WhatsApp"
4. **Ask for Help**: "What can you do?" or "Help me"

---

## 🐛 Quick Troubleshooting

**Backend won't start?**
```powershell
# Check if Python is installed
python --version

# Reinstall dependencies
pip install -r requirements.txt
```

**Frontend won't start?**
```powershell
# Check if Node is installed
node --version

# Reinstall dependencies
npm install
```

**Agent not working?**
- Check if Groq API key is set in `.env`
- Verify contact names match exactly
- Ensure default apps are configured

---

## 📚 Full Documentation

See `README_COMPLETE_GUIDE.md` for:
- Complete feature list
- All voice commands
- API documentation
- Advanced configuration
- Development guide

---

## 🎉 You're Ready!

Start automating your tasks with voice commands!

**Next Steps:**
1. Add your own contacts
2. Try all 10 agents
3. Explore multi-agent commands
4. Customize to your needs

---

**Questions?** Check the full documentation or create an issue.

**Happy Automating! 🚀**
