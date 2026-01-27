# 🤖 SwarAI - Multi-Agent AI Task Automation Assistant

<div align="center">

![SwarAI Logo](https://img.shields.io/badge/SwarAI-AI%20Assistant-blue?style=for-the-badge&logo=robot)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-15.5-black?style=flat-square&logo=next.js)](https://nextjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

**A sophisticated multi-agent AI system powered by CrewAI, LangChain, and Groq LLM**

[Features](#-features) • [Quick Start](#-quick-start) • [Installation](#-installation) • [Usage](#-usage) • [API](#-api-reference) • [Contributing](#-contributing)

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
- [License](#-license)

---

## 🌟 Overview

**SwarAI** is an advanced multi-agent AI task automation assistant that combines natural language processing, voice recognition, file management, and cross-platform communication into a unified, intelligent system.

### Key Highlights

- 🤖 **13 Specialized AI Agents** for different tasks
- 🎤 **Voice Recognition** with multiple engines (Google Speech, Whisper AI)
- 🗣️ **Text-to-Speech** with multiple TTS engines (Edge TTS, gTTS, Coqui)
- 📱 **WhatsApp Integration** for automated messaging
- 📁 **Intelligent File Search** with fuzzy matching
- 🔄 **Multi-Agent Orchestration** using CrewAI
- 🌐 **Modern Web Interface** built with Next.js
- 🚀 **FastAPI Backend** with WebSocket support
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

#### 2. **Voice Recognition & TTS**
- **Speech-to-Text**: Google Speech Recognition, Whisper AI
- **Text-to-Speech**: Microsoft Edge TTS, Google TTS, Coqui TTS, pyttsx3
- Multi-language support (English variants)
- Noise reduction and ambient adjustment
- Real-time voice processing

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
   GROQ_MODEL=llama-3.1-70b-versatile

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

2. **Configure environment (optional):**
   ```bash
   # Create .env.local if needed
   echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
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

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GROQ_API_KEY` | Groq API key for LLM | - | ✅ Yes |
| `GROQ_MODEL` | Groq model to use | `llama-3.1-70b-versatile` | No |
| `FASTAPI_HOST` | Backend host | `0.0.0.0` | No |
| `FASTAPI_PORT` | Backend port | `8000` | No |

#### Voice & Speech

| Variable | Description | Default |
|----------|-------------|---------|
| `TTS_ENGINE` | TTS engine (edge/gtts/coqui/pyttsx3) | `edge` |
| `SWARAI_VOICE` | Voice for TTS | `en-US-AriaNeural` |
| `ENABLE_VOICE_FEEDBACK` | Enable voice responses | `true` |
| `SPEECH_TIMEOUT` | Speech recognition timeout (seconds) | `7` |
| `SPEECH_PHRASE_TIME_LIMIT` | Max phrase duration (seconds) | `15` |

#### Database

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URL` | MongoDB connection string | `mongodb://localhost:27017` |
| `MONGODB_DATABASE` | Database name | `swarai_assistant` |
| `CONVERSATION_MEMORY_LIMIT` | Max conversation history | `50` |

#### Agent Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `AGENT_TEMPERATURE` | LLM temperature | `0.1` |
| `MAX_RESPONSE_TOKENS` | Max tokens in response | `1000` |

---

## 💻 Usage

### Voice Commands

#### WhatsApp
```
"Send WhatsApp to Jay: Hello, how are you?"
"Message Mom: I'll be late for dinner"
"WhatsApp Vijay: Can we reschedule the meeting?"
```

#### File Search
```
"Find my presentation"
"Search for report.pdf"
"Open the latest invoice"
"Find photos from last week"
```

#### System Control
```
"Set volume to 50%"
"Increase brightness"
"Check battery status"
"What's my system info?"
```

#### Conversation
```
"Hello SwarAI!"
"What can you do?"
"Help me with my tasks"
"Tell me a joke"
```

### API Usage

#### Process Command

```bash
curl -X POST http://localhost:8000/process-command \
  -H "Content-Type: application/json" \
  -d '{"command": "Send WhatsApp to Jay: Hello!"}'
```

#### Text-to-Speech

```bash
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from SwarAI!"}'
```

#### WebSocket Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};

ws.send(JSON.stringify({
  type: 'command',
  data: { command: 'Hello SwarAI!' }
}));
```

---

## 🤖 AI Agents

### Available Agents

| Agent | Description | Capabilities |
|-------|-------------|--------------|
| **WhatsApp** | Message automation | Send messages, contact search, URL generation |
| **FileSearch** | File management | Search files, open files, fuzzy matching |
| **Conversation** | Natural dialogue | Context-aware chat, personality, memory |
| **System Control** | System operations | Volume, brightness, battery, system info |
| **Email** | Email automation | Compose, send emails (Gmail integration) |
| **Calendar** | Calendar management | Create events, reminders (Google Calendar) |
| **Payment** | Payment processing | PayPal, Google Pay, UPI integration |
| **WebSearch** | Web searching | Google, Bing, DuckDuckGo, YouTube |
| **Phone** | Phone operations | Make calls, SMS (platform-dependent) |
| **App Launcher** | Application control | Launch apps, manage windows |
| **Screenshot** | Screen capture | Take screenshots, save images |
| **Task** | Task management | Create, manage tasks and reminders |
| **Multi-Task** | Workflow orchestration | Complex multi-step operations |

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
    "whatsapp_url": "https://wa.me/919321781905?text=Hello!"
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

<div align="center">

**Made with ❤️ by the SwarAI Team**

⭐ Star us on GitHub if you find this helpful!

[⬆ Back to Top](#-swarai---multi-agent-ai-task-automation-assistant)

</div>