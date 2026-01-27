# 🤖 AI Task Automation Assistant - Next.js Frontend

A beautiful, modern web interface for the AI Task Automation Assistant with voice recognition, real-time backend communication, and multi-agent support.

## ✨ Features

### 🎤 **Enhanced Voice Recognition**
- **Browser-based speech recognition** (Chrome, Edge, Firefox)
- **Multi-language support** (en-US, en-IN, en-GB, en-AU)
- **Real-time voice commands** with visual feedback
- **Fallback text input** for broader compatibility

### 🚀 **Modern Interface**
- **Beautiful gradient UI** with Tailwind CSS
- **Dark/Light mode** automatic detection
- **Responsive design** for all devices
- **Real-time status indicators**
- **Animated interactions** and smooth transitions

### 🤝 **Multi-Agent System**
- **WhatsApp Agent**: Send messages via voice/text
- **Call Agent**: Voice call automation (coming soon)
- **Calendar Agent**: Event management (coming soon)
- **File Agent**: File operations (coming soon)
- **Search Agent**: Web search capabilities (coming soon)

### 📊 **Command History & Analytics**
- **Real-time command tracking**
- **Success/failure indicators**
- **Agent attribution**
- **WhatsApp deep links**
- **Timestamp tracking**

## 🏗️ Architecture

```
┌─────────────────┐    HTTP/REST    ┌──────────────────┐
│   Next.js       │ ◄──────────────► │   FastAPI        │
│   Frontend      │    Port 3000     │   Backend        │
│   (React/TS)    │                  │   Port 8000      │
└─────────────────┘                  └──────────────────┘
         │                                    │
         │                                    │
         ▼                                    ▼
┌─────────────────┐                  ┌──────────────────┐
│  Browser APIs   │                  │  Agent Manager   │
│  - Speech Rec   │                  │  - WhatsApp      │
│  - Web Audio    │                  │  - LangGraph     │
│  - LocalStorage │                  │  - Groq LLM      │
└─────────────────┘                  └──────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.8+ with virtual environment
- **Modern web browser** (Chrome recommended for best speech recognition)

### 1. Start the Backend (FastAPI)
```bash
# Activate your Python virtual environment
# Navigate to the project root
cd "C:\\Users\\SURAJ\\Documents\\5clear chatapp\\Major Project BE"

# Start the FastAPI backend
python main.py
# Or use the startup script:
start_backend_nextjs.bat
```
Backend will be available at: **http://localhost:8000**

### 2. Start the Frontend (Next.js)
```bash
# In a new terminal, navigate to the frontend directory
cd "C:\\Users\\SURAJ\\Documents\\5clear chatapp\\Major Project BE\\ai-assistant-frontend"

# Install dependencies (first time only)
npm install

# Start the development server
npm run dev
# Or use the startup script from project root:
start_frontend_nextjs.bat
```
Frontend will be available at: **http://localhost:3000**

## 🎯 Usage Guide

### 🎤 **Voice Commands**
1. **Click "Start Voice Command"** button
2. **Wait for the red "Listening..."** indicator
3. **Speak clearly**: "Send WhatsApp to Jay: Hello how are you"
4. **Watch the magic happen!** ✨

### ⌨️ **Text Commands**
1. **Type in the text input**: "Message Mom: I'll be late today"
2. **Press Enter** or click **Send**
3. **View results** in the command history

### 📱 **Supported Commands**
```
🟢 WhatsApp Messages:
• "Send WhatsApp to Jay: Hello how are you"
• "Message Mom: I'll be late today"  
• "WhatsApp Vijay: Meeting at 5 PM"

🔴 Coming Soon:
• "Call John Smith"
• "Schedule meeting tomorrow 3 PM"
• "Search for Python tutorials"
• "Open project.pdf"
```

## 🛠️ Technology Stack

### Frontend (Next.js)
- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Speech**: Web Speech API
- **HTTP Client**: Fetch API

### Backend (FastAPI) 
- **Framework**: FastAPI with Uvicorn
- **Language**: Python 3.8+
- **AI/LLM**: LangChain + LangGraph + Groq
- **Agents**: Multi-agent coordination (MCP)
- **Database**: In-memory (expandable)

### Communication
- **Protocol**: HTTP REST APIs
- **Format**: JSON
- **Ports**: Frontend:3000 ↔ Backend:8000
- **CORS**: Enabled for local development

## 📁 Project Structure

```
📦 Major Project BE/
├── 🎨 ai-assistant-frontend/     # Next.js Frontend
│   ├── src/app/
│   │   ├── page.tsx             # Main AI Assistant Interface
│   │   ├── layout.tsx           # App Layout & Metadata
│   │   └── globals.css          # Global Styles
│   ├── package.json             # Frontend Dependencies
│   └── tailwind.config.js       # Tailwind Configuration
│
├── 🧠 agents/                   # AI Agents
│   ├── whatsapp_agent.py        # WhatsApp Integration
│   └── agent_manager.py         # Multi-Agent Coordinator
│
├── 🔧 utils/                    # Utilities
│   ├── enhanced_speech_processor.py  # Speech Recognition
│   └── speech_processor.py      # Basic Speech Utils
│
├── ⚙️ Configuration
│   ├── main.py                  # FastAPI Backend Server
│   ├── config.py                # Configuration Management
│   ├── .env                     # Environment Variables
│   └── requirements.txt         # Python Dependencies
│
└── 🚀 Startup Scripts
    ├── start_backend_nextjs.bat # Backend Startup
    └── start_frontend_nextjs.bat# Frontend Startup
```

## 🎨 UI Components

### 📊 **Status Dashboard**
- **Backend Connection**: Real-time health monitoring
- **Agent Availability**: Live agent status
- **Command Processing**: Visual feedback

### 🎤 **Voice Interface** 
- **Animated microphone button**
- **Real-time listening indicator**
- **Speech recognition feedback**
- **Error handling & fallbacks**

### 📱 **Command History**
- **Chronological command log**
- **Success/failure indicators**  
- **Agent attribution**
- **WhatsApp deep links**
- **Expandable details**

### 🤖 **Agent Cards**
- **Visual agent representation**
- **Status indicators**
- **Quick descriptions**
- **Hover effects**

## 🔧 Configuration

### Environment Variables (.env)
```env
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-70b-versatile

# Speech Recognition Settings  
SPEECH_TIMEOUT=7
SPEECH_PHRASE_TIME_LIMIT=15
SPEECH_ENERGY_THRESHOLD=300
SPEECH_PAUSE_THRESHOLD=0.8

# FastAPI Configuration
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
```

### Browser Requirements
- **Chrome/Chromium**: ✅ Full speech recognition
- **Edge**: ✅ Full speech recognition  
- **Firefox**: ⚠️ Limited speech support
- **Safari**: ⚠️ Limited speech support

## 🚨 Troubleshooting

### Backend Issues
```bash
❌ "Configuration validation failed"
   → Check your .env file and Groq API key

❌ "Port 8000 already in use" 
   → Kill existing process or change port

❌ "Agent not responding"
   → Check internet connection for Groq API
```

### Frontend Issues  
```bash
❌ "Cannot connect to backend"
   → Ensure FastAPI backend is running on port 8000
   
❌ "Speech recognition not working"
   → Use Chrome/Edge browser for best support
   → Check microphone permissions
   
❌ "Module not found" 
   → Run: npm install in frontend directory
```

## 🎯 Next Features

### 🔜 **Coming Soon**
- **📞 Call Agent**: Voice call automation
- **📅 Calendar Agent**: Smart scheduling  
- **📁 File Agent**: Voice file operations
- **🔍 Search Agent**: Intelligent web search
- **🎙️ Advanced TTS**: Server-side speech synthesis
- **📱 Mobile App**: React Native version

### 💡 **Enhancement Ideas**
- **Multi-user support** with authentication
- **Command templates** and shortcuts
- **Advanced voice training** and personalization
- **Integration plugins** (Slack, Discord, Email)
- **AI conversation** memory and context

## 🤝 Development

### Adding New Agents
1. **Create agent file** in `agents/` directory
2. **Implement LangGraph workflow**
3. **Register with agent manager** 
4. **Add UI components** in Next.js
5. **Test integration** end-to-end

### Extending Voice Commands
1. **Update intent detection** in agent manager
2. **Add command patterns** to recognition
3. **Implement backend logic**
4. **Update frontend UI** for new features

## 📄 License

This is a final year major project for educational purposes.

---

## 🎉 **Ready to Use!**

Your AI Task Automation Assistant with beautiful Next.js interface is ready! 

**Start the backend**, **launch the frontend**, and **experience voice-powered task automation** with a modern, responsive web interface! 🚀✨
