<div align="center">

# 🤖 SwarAI

### Multi-Agent AI Task Automation Assistant

<p align="center">
  <img src="https://img.shields.io/badge/SwarAI-AI%20Assistant-6366f1?style=for-the-badge&logo=robot&logoColor=white" alt="SwarAI" />
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" /></a>
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" /></a>
  <a href="https://nextjs.org/"><img src="https://img.shields.io/badge/Next.js-15.5-000000?style=for-the-badge&logo=next.js&logoColor=white" alt="Next.js" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License" /></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/CrewAI-0.86+-FF6B6B?style=flat-square&logo=ai&logoColor=white" alt="CrewAI" />
  <img src="https://img.shields.io/badge/LangChain-1.2+-1C3C3C?style=flat-square&logo=chainlink&logoColor=white" alt="LangChain" />
  <img src="https://img.shields.io/badge/Groq-LLM-F55036?style=flat-square&logo=ai&logoColor=white" alt="Groq" />
  <img src="https://img.shields.io/badge/MongoDB-Optional-47A248?style=flat-square&logo=mongodb&logoColor=white" alt="MongoDB" />
</p>

<h4>A sophisticated multi-agent AI system powered by CrewAI, LangChain, and Groq LLM</h4>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-usage">Usage</a> •
  <a href="#-api-reference">API</a> •
  <a href="#-recent-improvements--new-features">What's New</a> •
  <a href="#-contributing">Contributing</a>
</p>

</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [AI Agents](#-ai-agents)
- [API Reference](#-api-reference)
- [Development](#-development)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [Recent Improvements](#-recent-improvements--new-features)
- [Roadmap](#-roadmap)
- [License](#-license)

---

## 🌟 Overview

**SwarAI** is an advanced multi-agent AI task automation assistant that combines natural language processing, voice recognition, file management, and cross-platform communication into a unified, intelligent system.

### Key Highlights

- 🤖 **13 Specialized AI Agents** for different tasks
- 🚀 **65+ Application Launchers** including Windows apps, browsers, Office suite, and development tools
- 🌐 **15+ Website Quick Access** to popular platforms and services
- 🎤 **Voice Recognition** with multiple engines (Google Speech, Whisper AI)
- 🗣️ **Text-to-Speech** with intelligent speech filtering and context-aware output
- 📱 **WhatsApp Integration** with fuzzy contact matching and smart message handling
- 📁 **Intelligent File Search** with fuzzy matching, multi-location scanning, and latest file detection
- 📧 **AI-Powered Email** with automatic content generation and subject correction
- ⚙️ **System Control** (11 operations): Volume, brightness, battery, lock, power management
- 🧠 **Smart Intent Detection** with AI Enhancement Layer (auto-fixes typos and improves clarity)
- 🔄 **Multi-Agent Orchestration** using CrewAI for complex workflows
- 🌐 **Modern Web Interface** with dynamic animations, login system, and profile settings
- 🔐 **Authentication** with JWT tokens, Google OAuth, and protected routes
- 🚀 **FastAPI Backend** with WebSocket support and real-time processing
- 💾 **Conversation Memory** with MongoDB (optional)

---

## ✨ Features

### 🎯 Core Capabilities

#### 1. **Conversational AI**

- Natural language understanding with context awareness
- Personality-driven responses
- Multi-turn conversation support
- Intent classification and routing
- Emotional intelligence
- **AI Enhancement Layer**: Automatically improves command clarity and fixes typos using Groq LLM

#### 2. **Voice Recognition & TTS**

- **Speech-to-Text**: Google Speech Recognition, Whisper AI
- **Text-to-Speech**: Microsoft Edge TTS, Google TTS, Coqui TTS, pyttsx3
- Multi-language support (English variants)
- Noise reduction and ambient adjustment
- Real-time voice processing
- Context-aware speech filtering (removes URLs, paths, technical jargon)

#### 3. **WhatsApp Automation**

- Send messages via voice or text commands
- Contact management with fuzzy search
- WhatsApp URL generation (wa.me format)
- Natural language command parsing
- Multiple command pattern support

#### 4. **File Management**

- Cross-platform file search (Windows, macOS, Linux)
- Fuzzy matching algorithm
- Recursive directory searching
- File operations: search, open, share
- Performance-optimized scanning

#### 5. **System Control**

- Volume control (Windows with pycaw)
- Brightness adjustment
- Battery status monitoring
- System information retrieval
- Application launching

#### 6. **Multi-Agent Orchestration**

- CrewAI-powered agent coordination
- Complex workflow execution
- Task delegation and routing
- Error recovery and fallbacks
- Parallel task processing

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Voice UI     │  │ Agent Cards  │  │ Results      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/WebSocket
┌────────────────────────┴────────────────────────────────────┐
│                   Backend (FastAPI)                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Agent Manager (MCP)                      │   │
│  │  - Intent Detection  - Agent Routing  - Workflows    │   │
│  └──────────────────────────────────────────────────────┘   │
│                         │                                    │
│  ┌──────────────────────┴──────────────────────────────┐   │
│  │              Specialized Agents                      │   │
│  │  WhatsApp │ FileSearch │ Conversation │ System      │   │
│  │  Email │ Calendar │ Payment │ WebSearch │ ...       │   │
│  └──────────────────────────────────────────────────────┘   │
│                         │                                    │
│  ┌──────────────────────┴──────────────────────────────┐   │
│  │           CrewAI Orchestration Layer                 │   │
│  │  - Multi-Agent Coordination                          │   │
│  │  - Task Delegation                                   │   │
│  │  - Workflow Management                               │   │
│  └──────────────────────────────────────────────────────┘   │
│                         │                                    │
│  ┌──────────────────────┴──────────────────────────────┐   │
│  │              LLM Integration (Groq)                  │   │
│  │  LangChain │ LangGraph │ Groq LLM │ Context Memory  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

#### Backend

- **Framework**: FastAPI 0.115+
- **AI/ML**:
  - CrewAI 0.86+ (Multi-agent orchestration)
  - LangChain 1.2+ (AI framework)
  - LangGraph 1.0+ (Stateful workflows)
  - Groq LLM (Language model)
- **Speech**:
  - SpeechRecognition 3.10+
  - gTTS 2.5+
  - pydub 0.25+
  - pygame 2.5+
- **Database**:
  - MongoDB (via pymongo/motor)
- **Server**: Uvicorn (ASGI)

#### Frontend

- **Framework**: Next.js 15.5
- **UI**: React 19, TailwindCSS 4
- **State**: Zustand
- **Queries**: TanStack Query
- **Components**: Radix UI, Framer Motion
- **Icons**: Lucide React

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Node.js 18+ and npm
- Groq API Key ([Get one free](https://console.groq.com/))
- MongoDB (optional, for conversation memory)

### 1. Clone the Repository

```bash
git clone https://github.com/shashankpc7746/SwarAI.git
cd SwarAI
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### 3. Frontend Setup

```bash
cd frontend
npm install --legacy-peer-deps
```

### 4. Run the Application

**Terminal 1 - Backend:**

```bash
cd backend
python main.py
```

**Terminal 2 - Frontend:**

```bash
cd frontend
npm run dev
```

### 5. Access the Application

- **Frontend UI**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 📦 Installation

### Detailed Backend Installation

1. **Create and activate virtual environment:**

   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

2. **Install Python dependencies:**

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**

   ```bash
   cp .env.example .env
   ```

4. **Edit `.env` file:**

   ```env
   # Required
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=llama-3.3-70b-versatile

   # Google OAuth (Get from https://console.cloud.google.com/apis/credentials)
   GOOGLE_CLIENT_ID=your_google_client_id_here.apps.googleusercontent.com

   # Optional
   MONGODB_URL=mongodb://localhost:27017
   MONGODB_DATABASE=swarai_assistant
   TTS_ENGINE=edge  # edge, gtts, coqui, pyttsx3
   ENABLE_VOICE_FEEDBACK=true
   ```

### Detailed Frontend Installation

1. **Install Node.js dependencies:**

   ```bash
   cd frontend
   npm install --legacy-peer-deps
   ```

2. **Configure environment variables:**

   Create `frontend/.env.local` file:

   ```bash
   # Create .env.local
   cp .env.example .env.local
   ```

   Edit `.env.local` and add:

   ```env
   # Backend API URL
   NEXT_PUBLIC_API_URL=http://localhost:8000

   # Google OAuth (Get from https://console.cloud.google.com/apis/credentials)
   NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_google_client_id_here.apps.googleusercontent.com
   ```

### Optional Dependencies

For full system control features:

```bash
# Windows volume control
pip install pycaw comtypes

# System monitoring
pip install psutil

# Brightness control
pip install screen-brightness-control
```

---

## ⚙️ Configuration

### Environment Variables

#### Core Configuration

| Variable       | Description          | Default                   | Required |
| -------------- | -------------------- | ------------------------- | -------- |
| `GROQ_API_KEY` | Groq API key for LLM | -                         | ✅ Yes   |
| `GROQ_MODEL`   | Groq model to use    | `llama-3.1-70b-versatile` | No       |
| `FASTAPI_HOST` | Backend host         | `0.0.0.0`                 | No       |
| `FASTAPI_PORT` | Backend port         | `8000`                    | No       |

#### Voice & Speech

| Variable                   | Description                          | Default            |
| -------------------------- | ------------------------------------ | ------------------ |
| `TTS_ENGINE`               | TTS engine (edge/gtts/coqui/pyttsx3) | `edge`             |
| `SWARAI_VOICE`             | Voice for TTS                        | `en-US-AriaNeural` |
| `ENABLE_VOICE_FEEDBACK`    | Enable voice responses               | `true`             |
| `SPEECH_TIMEOUT`           | Speech recognition timeout (seconds) | `7`                |
| `SPEECH_PHRASE_TIME_LIMIT` | Max phrase duration (seconds)        | `15`               |

#### Database

| Variable                    | Description               | Default                     |
| --------------------------- | ------------------------- | --------------------------- |
| `MONGODB_URL`               | MongoDB connection string | `mongodb://localhost:27017` |
| `MONGODB_DATABASE`          | Database name             | `swarai_assistant`          |
| `CONVERSATION_MEMORY_LIMIT` | Max conversation history  | `50`                        |

#### Authentication

| Variable                       | Description                           | Default | Required |
| ------------------------------ | ------------------------------------- | ------- | -------- |
| `GOOGLE_CLIENT_ID`             | Google OAuth 2.0 Client ID (backend)  | -       | ✅ Yes   |
| `NEXT_PUBLIC_GOOGLE_CLIENT_ID` | Google OAuth 2.0 Client ID (frontend) | -       | ✅ Yes   |

> **Get Google Client ID**: https://console.cloud.google.com/apis/credentials
>
> - Create OAuth 2.0 Client ID
> - Application type: Web application
> - Authorized JavaScript origins: `http://localhost:3000`
> - Authorized redirect URIs: `http://localhost:3000/auth/callback`

#### Agent Configuration

| Variable              | Description            | Default |
| --------------------- | ---------------------- | ------- |
| `AGENT_TEMPERATURE`   | LLM temperature        | `0.1`   |
| `MAX_RESPONSE_TOKENS` | Max tokens in response | `1000`  |

---

## 💻 Usage

### Voice Commands

#### WhatsApp

```
"Send WhatsApp to Jay: Hello, how are you?"
"Message Mom: I'll be late for dinner"
"WhatsApp Vijay: Can we reschedule the meeting?"
"WhatsApp Shivam clg about project deadline"
```

#### Email

```
"Draft email to Jay about meeting tomorrow"
"Send email to hr@company.com subject job application"
"Compose email to Vijay Sharma about internship"
"Email my professor regarding project submission"
```

#### File Search

```
"Find my presentation"
"Search for report.pdf"
"Open the latest invoice"
"Open pdf" (opens newest PDF from Downloads)
"Find NPTEL certificates"
```

#### Information Queries

```
"Who is Shashank?"
"Tell me about Jay"
"What do you know about the Harappan civilization?"
"Give me details about quantum computing"
```

#### System Control

```
"Increase volume"
"Volume up"
"Make it louder"
"Check battery status"
"What's the time?"
```

#### Conversation

```
"Hello SwarAI!"
"What can you do?"
"Help me with my tasks"
"How's your day going?"
```

#### Calendar

```
"What's my schedule for today?"
"Show me upcoming events"
"Add meeting on Friday at 3 PM"
"Do I have any appointments tomorrow?"
```

#### Web Search

```
"Search for latest AI news"
"Show me Python tutorials"
"Look up weather in Mumbai"
"Find information about quantum computing"
```

#### Screenshot

```
"Take a screenshot"
"Capture my screen"
"Save current screen as image"
```

"Tell me a joke"

````

### API Usage

#### Process Command

```bash
curl -X POST http://localhost:8000/process-command \
  -H "Content-Type: application/json" \
  -d '{"command": "Send WhatsApp to Jay: Hello!"}'
````

#### Text-to-Speech

```bash
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from SwarAI!"}'
```

#### WebSocket Connection

```javascript
const ws = new WebSocket("ws://localhost:8000/ws");

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("Received:", data);
};

ws.send(
  JSON.stringify({
    type: "command",
    data: { command: "Hello SwarAI!" },
  }),
);
```

---

## 🤖 AI Agents

### All 13 Specialized Agents

| Agent              | Description                    | Key Capabilities                                                          |
| ------------------ | ------------------------------ | ------------------------------------------------------------------------- |
| **App Launcher**   | Application & website control  | 65+ apps (Office, browsers, dev tools), 15+ websites, phonetic correction |
| **WhatsApp**       | Message automation             | wa.me links, fuzzy matching, 10+ contacts, quote removal                  |
| **File Search**    | Cross-platform file management | Fuzzy search, multi-location scan, MIME detection, open/share             |
| **Conversation**   | Natural AI dialogue            | Context-aware chat, personality, multi-turn, Groq LLM powered             |
| **System Control** | System operations              | Volume, brightness, battery, time, lock, shutdown, restart, sleep         |
| **Email**          | Email automation               | AI content generation, Gmail integration, subject correction              |
| **Calendar**       | Event scheduling               | Create events, Google Calendar, relative time parsing                     |
| **Payment**        | Payment processing             | PayPal, Google Pay, Paytm, PhonePe, UPI, multi-currency                   |
| **Web Search**     | Internet searching             | Google, Bing, DuckDuckGo, YouTube, Scholar, Maps, Images                  |
| **Phone**          | Call operations                | Fuzzy contact search, tel: protocol, Skype integration                    |
| **Screenshot**     | Screen capture                 | PIL ImageGrab, multi-monitor, OneDrive save, PNG timestamps               |
| **Task**           | To-do management               | Add/list/complete/delete, priorities, due dates, JSON storage             |
| **Multi-Task**     | Workflow orchestration         | CrewAI coordination, agent chaining, file+communication flows             |

### Statistics

- **Total Agents**: 13 | **Apps**: 65+ | **Websites**: 15+ | **Search Engines**: 7 | **System Actions**: 11 | **Payment Platforms**: 4
- **Powered by**: Groq LLM (llama-3.3-70b-versatile), LangGraph, CrewAI, FastAPI, MongoDB (optional)

### Agent Architecture

Each agent follows a consistent pattern:

```python
class Agent:
    def __init__(self):
        self.llm = ChatGroq(...)  # Groq LLM
        self.tools = [...]        # Agent-specific tools

    def process_command(self, user_input: str) -> Dict:
        # 1. Parse command
        # 2. Execute action
        # 3. Return result
        pass
```

---

## 📚 API Reference

### REST Endpoints

#### `POST /process-command`

Process a text or voice command.

**Request:**

```json
{
  "command": "Send WhatsApp to Jay: Hello!",
  "use_voice": false
}
```

**Response:**

```json
{
  "success": true,
  "message": "WhatsApp message ready for Jay!",
  "agent": "whatsapp",
  "data": {
    "whatsapp_url": "https://wa.me/911234567890?text=Hello!"
  }
}
```

#### `POST /tts`

Convert text to speech.

**Request:**

```json
{
  "text": "Hello from SwarAI!",
  "engine": "edge"
}
```

**Response:**

```json
{
  "success": true,
  "audio_file": "path/to/audio.mp3"
}
```

#### `GET /health`

Check API health status.

**Response:**

```json
{
  "status": "healthy",
  "version": "2.0.0",
  "agents_loaded": 13,
  "llm_available": true
}
```

#### `GET /agents`

List all available agents.

**Response:**

```json
{
  "agents": [
    {
      "name": "WhatsApp Agent",
      "status": "active",
      "capabilities": ["send_message", "contact_search"]
    },
    ...
  ]
}
```

### WebSocket Events

#### Client → Server

```json
{
  "type": "command",
  "data": {
    "command": "Hello SwarAI!"
  }
}
```

#### Server → Client

```json
{
  "type": "response",
  "data": {
    "message": "Hello! How can I help you?",
    "agent": "conversation"
  }
}
```

---

## 🛠️ Development

### Project Structure

```
SwarAI/
├── backend/
│   ├── agents/                 # AI Agents
│   │   ├── __init__.py
│   │   ├── agent_manager.py    # Main coordinator
│   │   ├── whatsapp_agent.py
│   │   ├── filesearch_agent.py
│   │   ├── conversation_agent.py
│   │   └── ...
│   ├── utils/                  # Utilities
│   │   ├── enhanced_speech_processor.py
│   │   ├── conversational_tts.py
│   │   ├── conversation_memory.py
│   │   └── ...
│   ├── config.py               # Configuration
│   ├── main.py                 # FastAPI server
│   ├── crew_main.py            # CrewAI server
│   ├── crew_config.py          # CrewAI configuration
│   ├── requirements.txt        # Python dependencies
│   └── .env.example            # Environment template
├── frontend/
│   ├── src/
│   │   ├── app/                # Next.js app
│   │   ├── components/         # React components
│   │   └── hooks/              # Custom hooks
│   ├── package.json
│   └── next.config.ts
├── .gitignore
└── README.md
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Style

```bash
# Python (Black, isort)
cd backend
black .
isort .

# TypeScript (ESLint, Prettier)
cd frontend
npm run lint
npm run format
```

### Adding a New Agent

1. Create agent file in `backend/agents/`:

```python
from langchain.tools import BaseTool
from langchain_groq import ChatGroq

class MyAgent:
    def __init__(self):
        self.llm = ChatGroq(...)

    def process_command(self, user_input: str):
        # Implementation
        pass
```

2. Register in `agent_manager.py`:

```python
from agents.my_agent import MyAgent

self.my_agent = MyAgent()
```

3. Add routing logic in `process_command()`.

---

## 🐛 Troubleshooting

### Common Issues

#### 1. **ModuleNotFoundError: No module named 'streamlit'**

**Solution:**

```bash
pip install streamlit pycaw comtypes psutil screen-brightness-control
```

#### 2. **MongoDB Connection Failed**

**Solution:**
The app works without MongoDB (uses in-memory storage). To fix:

```bash
# Install MongoDB locally or use MongoDB Atlas
# Update MONGODB_URL in .env
```

#### 3. **Voice Recognition Not Working**

**Solution:**

```bash
# Install audio dependencies
pip install pyaudio  # May need system libraries

# Windows: Download PyAudio wheel
# Linux: sudo apt-get install portaudio19-dev python3-pyaudio
# Mac: brew install portaudio
```

#### 4. **Frontend Won't Start**

**Solution:**

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
npm run dev
```

#### 5. **GROQ_API_KEY Error**

**Solution:**

1. Get API key from https://console.groq.com/
2. Add to `backend/.env`:
   ```env
   GROQ_API_KEY=your_actual_key_here
   ```

### Debug Mode

Enable debug logging:

```env
# .env
LOG_LEVEL=DEBUG
DEBUG_MODE=true
```

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Ways to Contribute

1. **Report Bugs**: Open an issue with details
2. **Suggest Features**: Share your ideas
3. **Submit Pull Requests**: Fix bugs or add features
4. **Improve Documentation**: Help others understand
5. **Share Feedback**: Tell us what works and what doesn't

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Test thoroughly**
5. **Commit with clear messages**:
   ```bash
   git commit -m "Add amazing feature"
   ```
6. **Push to your fork**:
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

### Code Guidelines

- Follow PEP 8 for Python
- Use TypeScript for frontend
- Write clear commit messages
- Add tests for new features
- Update documentation

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **CrewAI** - Multi-agent orchestration framework
- **LangChain** - AI application framework
- **Groq** - Fast LLM inference
- **FastAPI** - Modern Python web framework
- **Next.js** - React framework
- **All contributors** - Thank you!

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/shashankpc7746/SwarAI/issues)
- **Discussions**: [GitHub Discussions](https://github.com/shashankpc7746/SwarAI/discussions)
- **Email**: [Your Email]

---

## 🗺️ Roadmap

### Planned Features

- [ ] Mobile app (React Native)
- [ ] Voice cloning
- [ ] Custom agent creation UI
- [ ] Plugin system
- [ ] Cloud deployment guides
- [ ] Docker support
- [ ] Kubernetes manifests
- [ ] Advanced analytics
- [ ] Multi-language support
- [ ] Integration marketplace

---

## 🎉 Recent Improvements & New Features

### Version 3.1 - Google OAuth & UI Refinements (February 2026)

#### 🔐 Full Google OAuth Integration

- **Google Sign-In** fully implemented with `google-auth` library
- Backend token verification with Google API
- Automatic user creation from Google account (name + email)
- Profile picture syncing from Google accounts
- Seamless login experience with popup flow
- Secure JWT token generation after OAuth validation

**Setup**: Requires `GOOGLE_CLIENT_ID` in both backend and frontend `.env` files

#### ✨ Starfield Background System

**Removed**: Large aurora gradient orbs that made background feel crowded

**Added**:

- **50 moving star particles** - drift across screen in random directions
- **40 static twinkling stars** - pulse in/out with varying brightness
- 4 color variants (indigo, lavender, white, sky blue) with glow effects
- Optimized animations with `useMemo` for performance

**Result**: Clean, spacious night-sky aesthetic with subtle motion

#### 🎨 UI/UX Polish

- **Smaller cursor glow effect** - 250px/400px (was 500px/700px) for less distraction
- **Agent card hover overlay** - Examples appear as dark overlay inside card (fixed clipping issues)
- **Tap to Speak ambient glow** - Dual-layer animated color rings (indigo ↔ purple)
- **Swiper fixes** - Exactly 5 cards visible, centered 3rd card under voice button
- Fixed hover cut-off by adding internal padding to scrollable container

---

### Version 3.0 - Auth, UI Overhaul & Animations

#### 🔐 Authentication System

- Login page with name, email, age fields
- JWT-based session management with 7-day expiry
- Protected routes — main app requires authentication
- Profile settings modal (replaces dummy settings button)
- Google OAuth integration (frontend + backend)

#### 🎙️ Dynamic Voice Button Animations

- 3 orbital rings rotating at different speeds around the button
- 8 radial floating particles with staggered timing
- Pulsing gradient glow effect (blue ↔ purple)
- Animated box shadow cycling per state (ready/listening/processing)
- Mic icon float animation with spring physics
- Glowing "TAP TO SPEAK" text with animated text-shadow
- Triple expanding ripple effects during listening/processing
- Wobble effect on hover, smooth scale on tap

#### 🎨 UI Polish

- Restored original logo size with "SwarAI / Multi-Agent AI System" text
- Safari compatibility: `-webkit-backdrop-filter` for all glass classes
- Animated starfield background on main page and login
- Proper content spacing to prevent agent cards clipping

---

### Version 2.5 - Enhanced UX & Intelligence

#### 🎨 Refined Agent Card Interface

**Improvements:**

- Smoother hover animations (0.4s easing instead of instant)
- Removed zoom effect for cleaner interaction
- Fixed grid layout to prevent height synchronization issues
- Added GPU-accelerated animations with `will-change` properties
- Eliminated layout shake during hover
- Cards now expand independently without affecting others

**Result:** Professional, buttery-smooth card interactions with zero layout jank.

#### 🧠 Intelligent Intent Detection

**Problem:** Information queries like "who is Jay" were routing to file manager.

**Solution:** Enhanced intent detection with:

- Information query patterns: "who is", "tell me about", "what do you know about"
- File context validation (requires file-related keywords AND operations)
- Priority routing: Information queries → Conversation agent
- Preserved file operations: "find ownership document" → File manager

**Examples:**
✅ "who is Jay" → Conversation agent (answers about the person)
✅ "tell me about Shashank" → Conversation agent (information)
✅ "find ownership document" → File manager (actual file search)
✅ "open presentation.pdf" → File manager (file operation)

**Result:** Natural conversational queries get intelligent responses, not file search errors.

#### 📧 Robust Email Agent

**Improvements:**

- **Better Recipient Parsing:** Handles concatenated command words like "draftanemailtoVijaySharma"
- **Reliable Gmail Opening:** Proper URL encoding with UTF-8 support
- **AI Content Generation:** Automatically drafts professional emails (200-400 words)
- **Subject Grammar Correction:** Auto-capitalizes and formats subject lines
- **Validation:** Checks recipient validity before opening Gmail
- **Enhanced Logging:** Detailed debug output for troubleshooting

**Features:**

- AI-generated email bodies when content is not provided
- Professional tone with proper greetings and closings
- Smart truncation for long content (5000 char limit)
- Fallback handling if AI generation fails

**Result:** Reliable email composition every time, with professional AI-generated content.

#### 🗣️ Complete Speech Playback

**Problem:** Speech was cutting off mid-sentence for long responses.

**Solution:**

- Increased speech limit: 1000 → 2000 characters for conversations
- Smart truncation at sentence boundaries (finds last period)
- Prevents mid-word cuts with proper sentence completion

**Before:**

> "I've got a wealth of information on the Indus Valley Harappan civilization. The Harappans were a sophisticated Bronze Age civilization that thrived in the Indus Valley region, which is now modern-day Pakistan and northwestern India, from around 3300 to 1300 BCE. They're known for their impressive urban planning, architecture, and water management systems, as well as their unique writing system, which has yet to be fully deciphered. If you'd like, I can provide more specific information on their" ❌

**After:**

> "I've got a wealth of information on the Indus Valley Harappan civilization. The Harappans were a sophisticated Bronze Age civilization that thrived in the Indus Valley region, which is now modern-day Pakistan and northwestern India, from around 3300 to 1300 BCE. They're known for their impressive urban planning, architecture, and water management systems, as well as their unique writing system, which has yet to be fully deciphered." ✅

#### 🛑 Reliable Speech Stop Control

**Problem:** Speech continued after page refresh or clicking "Tap to Speak".

**Solution:** Enhanced stop mechanism with:

- Double-cancel pattern (immediate + 50ms delayed)
- State checking before cancellation
- 100ms delay before starting new recognition
- Cleanup on unmount, refresh, and navigation

**Result:** Speech always stops immediately when requested. Clean audio control.

#### ♿ Accessibility Improvements

**Added:**

- `aria-label` attributes to icon-only buttons
- Descriptive labels for screen readers
- Proper semantic HTML structure

**Complies with:** WCAG 2.1 Level AA standards

---

### Version 2.4 - UX Improvements

#### 🔊 Speech Control on Page Refresh

**Problem:** Speech would continue playing in background after page refresh.

**Solution:** Added cleanup handlers to stop speech immediately on:

- Page refresh
- Navigation away
- Tab close
- Component unmount

**Result:** Clean, professional user experience with controllable audio.

#### 📝 Concise Introduction Responses

**Problem:** Introduction responses were too long (45+ seconds).

**Solution:** Shortened to 2-3 sentences maximum with key capabilities only.

**Result:** Quick, clear introductions (~10 seconds) without overwhelming users.

---

### Version 2.3 - AI Grammar Correction

#### ✨ AI-Powered WhatsApp Message Grammar

Automatically improves grammar in all WhatsApp messages:

**Features:**

- Capitalizes first letter of sentences
- Adds proper punctuation (. ? !)
- Fixes grammar mistakes naturally
- Preserves conversational tone
- Smart context-aware punctuation

**Examples:**

```
"how are you" → "How are you?"
"i am coming home" → "I am coming home."
"meeting at 5" → "Meeting at 5."
"gonna be late" → "Gonna be late."
```

**Workflow Integration:**

```
Parse Command → AI Grammar Correction → Search Contact → Generate URL → Send
```

---

### Version 2.2 - Smart Features

#### 📁 Smart "Latest File" Detection

When you specify only a file type (without filename), SwarAI opens the most recent file of that type from Downloads.

**Examples:**

```bash
"open pdf" → Opens newest PDF from Downloads
"open word" → Opens latest .docx from Downloads
"open excel" → Opens latest .xlsx from Downloads
"open powerpoint" → Opens latest .pptx from Downloads
```

**Specific file search still works:**

```bash
"open NPTEL certificates" → Finds and opens specific file
```

---

### Version 2.1 - Enhanced Speech Quality

#### 🗣️ File Path Filtering

**Problem:** SwarAI was reading file paths in speech.

**Solution:** Intelligent removal of:

- Windows paths: `C:\Users\...`
- Unix paths: `/home/user/...`
- Path patterns: `Path: ...`
- Special symbols with paths

**Result:**

```
Before: "Successfully opened: NPTEL.pdf Path: C:\Users\Shashank Gupta\Downloads\NPTEL.pdf"
After: "Opened NPTEL.pdf"
```

#### 👋 Natural Greeting Flow

**Problem:** Redundant "Got it!" before greeting responses.

**Solution:** Skip acknowledgment for greetings (hi, hello, hey, good morning, etc.)

**Result:**

```
Before: "Got it!" → pause → "Hello, I'm SwarAI..."
After: "Hello, I'm SwarAI, nice to meet you..."
```

---

### Version 2.0 - Major UX Improvements

#### 🔍 Fuzzy Contact Name Matching

**Problem:** Required exact contact names, failing for variations.

**Solution:** Intelligent fuzzy matching that handles:

- Partial names: "Shivam" → Finds "Shivam Patel"
- Common suffixes: "clg", "college", "mam", "sir", "bro", "sis"
- First name only: "Jay" → Finds "Jay Sharma"
- Substring matching

**Examples:**

```
✅ "Shivam clg" → Finds "Shivam Patel"
✅ "Gitanjali mam" → Finds "Gitanjali"
✅ "Jay" → Finds "Jay Sharma"
```

#### 🎤 Intelligent Speech Filtering

**Problem:** SwarAI was reading URLs and technical content.

**Solution:** Smart filtering that removes:

- URLs: `https://wa.me/...`
- Phone numbers: `+919876543219`
- Technical instructions: "Click the link to send"
- Keeps full text in chat for visual reference

**Result:**

```
Before: "WhatsApp message ready for Gitanjali! Click the link to send: https://wa.me/+919876543219?text=..."
After: "WhatsApp message ready for Gitanjali. Opening WhatsApp now."
```

#### 📏 Context-Aware Speech Length

**Problem:** Speech cut off at 200 characters regardless of content.

**Solution:** Smart length limits based on content type:

| Agent Type   | Max Length | Purpose                   |
| ------------ | ---------- | ------------------------- |
| Conversation | 1000 chars | Full responses            |
| WebSearch    | 1000 chars | Complete information      |
| WhatsApp     | 100 chars  | Brief confirmations       |
| FileSearch   | 100 chars  | Quick feedback            |
| Email        | 100 chars  | Action confirmations      |
| Payment      | 100 chars  | Transaction confirmations |
| Default      | 500 chars  | Balanced                  |

**Result:** Full educational content and conversations, brief action confirmations.

---

### 🎯 Complete Filtering & Enhancement Pipeline

The speech system now applies intelligent filtering:

1. **Remove Emojis** - Clean visual symbols
2. **Remove URLs** - No "https colon slash slash"
3. **Remove File Paths** - No directory structures
4. **Remove Technical Patterns** - No wa.me links, phone numbers
5. **Remove Instructions** - No "Click here" messages
6. **Agent-Specific Simplification** - Context-aware brevity
7. **Context-Aware Length Limiting** - Appropriate for content type

---

### 🧪 Test the New Features

#### WhatsApp with Fuzzy Matching:

```
"send WhatsApp to Shivam clg that AI is working"
"message Gitanjali mam hello"
"WhatsApp Jay that meeting at 5"
```

#### Smart File Opening:

```
"open pdf" → Opens latest PDF
"open NPTEL certificates" → Opens specific file
```

#### Natural Conversations:

```
"hello" → Direct greeting (no "Got it!")
"give me details about Harappan civilization" → Full response
```

---

<div align="center">

**Made with ❤️ by the SwarAI Team**

⭐ Star us on GitHub if you find this helpful!

[⬆ Back to Top](#-swarai---multi-agent-ai-task-automation-assistant)

</div>
