# 🤖 Vaani - Enhanced Multi-Agent AI Assistant

A sophisticated conversational AI assistant powered by **CrewAI**, **Groq LLM**, and **LangGraph** with advanced voice recognition, intelligent file management, and seamless WhatsApp integration.

## 🌟 Project Overview

**Vaani** (named after the Sanskrit word for "voice") is a state-of-the-art multi-agent AI system that combines natural language processing, voice recognition, file system operations, and cross-platform communication into a unified, intelligent assistant.

### 🎯 Core Features

- **🗣️ Conversational AI**: Natural language understanding with Vaani personality
- **📱 WhatsApp Integration**: Voice/text message automation with contact management
- **📁 Intelligent File Search**: Cross-platform file operations with fuzzy matching
- **🔄 Multi-Agent Orchestration**: Complex workflow coordination using CrewAI
- **🎤 Enhanced Voice Recognition**: Multi-engine speech processing (Google + Whisper)
- **🌐 Modern Web Interface**: Next.js frontend with real-time WebSocket communication
- **📊 Streamlit Dashboard**: Alternative interface for system monitoring

## 🏗️ Architecture Deep Dive

### Backend Architecture (Python)

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│    FastAPI Server   │    │   Agent Manager     │    │  CrewAI Orchestra   │
│  - REST API         │◄──►│  - Intent Detection │◄──►│  - Multi-Agent      │
│  - WebSocket        │    │  - Agent Routing    │    │  - Workflow Coord   │
│  - CORS Config      │    │  - LangGraph Flow   │    │  - Task Execution   │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
         │                            │                            │
         │                            ▼                            ▼
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│  Enhanced Speech    │    │  Specialized Agents │    │   LLM Integration   │
│  - Multi-Engine STT │    │  - WhatsApp Agent   │    │   - Groq LLM Only   │
│  - Cross-Platform   │    │  - FileSearch Agent │    │   - LangChain       │
│  - TTS Systems      │    │  - Conversation AI  │    │   - Context Memory  │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

### Frontend Architecture (Next.js)

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│     UI Layer        │    │    Hooks Layer      │    │   Service Layer     │
│  - Voice Interface  │◄──►│  - useVoiceRec      │◄──►│  - Backend API      │
│  - Agent Cards      │    │  - useCrewAI        │    │  - WebSocket Conn   │
│  - Result Display   │    │  - useSound         │    │  - Error Handling   │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

## 📋 Technical Specifications

### Backend Components

#### 1. **Agent Manager (`agents/agent_manager.py`)**
- **Multi-Agent Coordinator (MCP)** using LangGraph
- **Intent Detection** with Groq LLM and rule-based patterns
- **Dynamic Agent Routing** based on command complexity
- **Multi-Agent Workflows** for complex tasks (file + WhatsApp)
- **Error Recovery** and graceful fallbacks

#### 2. **Specialized Agents**

**WhatsApp Agent (`agents/whatsapp_agent.py`)**
- Natural language command parsing
- Contact database with fuzzy matching
- WhatsApp URL generation (wa.me format)
- LangGraph workflow for stateful processing
- Multiple command patterns support

**FileSearch Agent (`agents/filesearch_agent.py`)**
- Cross-platform file system access (Windows/macOS/Linux)
- Fuzzy matching algorithm with scoring
- Recursive directory searching with performance optimization
- File operations: search, open, prepare for sharing
- Real file system integration with proper permissions

**Conversation Agent (`agents/conversation_agent.py`)**
- Vaani personality implementation
- Context-aware dialogue management
- Natural conversation flow with memory
- Intent classification and response generation
- Emotional intelligence and user guidance

#### 3. **CrewAI Integration (`crew_config.py`)**
- **Groq LLM Exclusive**: No OpenAI dependencies
- Multi-agent orchestration with specialized roles
- Task coordination and workflow management
- Error handling and fallback systems
- Complex workflow execution (file-to-WhatsApp sharing)

#### 4. **Enhanced Speech Processing (`utils/enhanced_speech_processor.py`)**
- **Multi-Engine Recognition**: Google Speech + Whisper AI
- **Cross-Platform Audio**: pygame, gtts, pydub support
- **Language Support**: en-US, en-IN, en-GB, en-AU
- **Noise Reduction** and ambient adjustment
- **Fallback Systems** for audio failures

### Frontend Components

#### 1. **Main Interface (`src/app/page.tsx`)**
- Modern React with TypeScript
- Framer Motion animations
- Voice recognition integration
- Real-time status indicators
- Conversation history management
- WhatsApp popup handling

#### 2. **Hooks (`src/hooks/`)**
- `useCrewAI.ts`: CrewAI backend integration with WebSocket
- `useVoiceRecognition.ts`: Browser speech recognition
- `useBackendApi.ts`: RESTful API communication
- `useSound.ts`: Audio feedback and TTS

#### 3. **Components (`src/components/`)**
- `AgentCard.tsx`: Interactive agent selection
- `VoiceVisualization.tsx`: Audio wave animations
- `ResultDisplay.tsx`: Response formatting
- `StatusIndicator.tsx`: System health monitoring

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.11+** (recommended)
- **Node.js 18+** and npm
- **Groq API Key** ([Get it here](https://console.groq.com/))

### Installation

1. **Clone and Setup**
```bash
git clone <repository-url>
cd "Major Project BE"
```

2. **Automated Setup**
```bash
# Run the enhanced setup script
setup_enhanced_vaani.bat
```

3. **Configure Environment**
```bash
# Edit backend/.env with your Groq API key
GROQ_API_KEY=your_actual_groq_api_key_here
GROQ_MODEL=llama-3.1-70b-versatile
```

4. **Start Services**
```bash
# Terminal 1: Backend
start_vaani_backend.bat

# Terminal 2: Frontend
cd frontend && npm run dev
```

5. **Access Application**
- **Next.js UI**: http://localhost:3000
- **Streamlit Dashboard**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs

## 💬 Command Examples

### Natural Conversation
```
🗣️ "Hello Vaani!"
🗣️ "What can you do?"
🗣️ "Help me with my tasks"
🗣️ "Thank you for your help"
```

### WhatsApp Messaging
```
🗣️ "Send WhatsApp to Mom: I'm coming home"
🗣️ "Tell dad I'll be late for dinner"
🗣️ "Message jay about the meeting tomorrow"
🗣️ "WhatsApp vijay: Can we reschedule?"
```

### File Operations
```
🗣️ "Find my photos"
🗣️ "Search for report.pdf"
🗣️ "Open ownership document"
🗣️ "Show me Excel files"
```

### Multi-Agent Workflows
```
🗣️ "Send my report to boss on WhatsApp"
🗣️ "Find presentation.pptx and share with team"
🗣️ "Search for ownership document and send to jay"
```

## 🔧 Configuration Details

### Backend Configuration (`backend/.env`)
```env
# AI Configuration
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-70b-versatile

# Server Configuration
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000

# Speech Configuration
SPEECH_TIMEOUT=7
SPEECH_PHRASE_TIME_LIMIT=15

# Agent Configuration
AGENT_TEMPERATURE=0.1
MAX_RESPONSE_TOKENS=1000
```

### Frontend Configuration (`frontend/package.json`)
- **Framework**: Next.js 15.5.0 with Turbopack
- **UI**: Tailwind CSS with Framer Motion
- **State**: Zustand for state management
- **Communication**: WebSocket + REST API
- **Audio**: Web Speech API integration

## 📊 Performance Metrics

### Response Times
- **Conversation**: < 1 second
- **File Search**: < 2 seconds  
- **WhatsApp**: < 1 second
- **Multi-Agent**: < 3 seconds

### Reliability Features
- **Error Recovery**: Graceful handling of all failure scenarios
- **Fallback Systems**: Multiple backup approaches for critical functions
- **User Guidance**: Clear, helpful error messages
- **Logging**: Comprehensive system monitoring

## 🛠️ Development Guide

### Adding New Agents

1. **Create Agent File**
```python
# backend/agents/new_agent.py
class NewAgent:
    def __init__(self):
        self.llm = ChatGroq(...)
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        # Implement LangGraph workflow
        pass
    
    def process_command(self, user_input: str) -> Dict[str, Any]:
        # Process user command
        pass
```

2. **Register Agent**
```python
# backend/agents/agent_manager.py
self.agents = {
    "whatsapp": whatsapp_agent,
    "conversation": conversation_agent,
    "filesearch": filesearch_agent,
    "new_agent": new_agent  # Add here
}
```

3. **Update Frontend**
```typescript
// frontend/src/app/page.tsx
const agents = [
  // ... existing agents
  {
    id: 'new_agent',
    name: 'New Agent',
    description: 'Agent description',
    icon: Icon,
    color: 'from-color-to-color'
  }
];
```

### Extending Workflows

```python
# In agent_manager.py
def _handle_multi_agent_workflow(self, user_input: str) -> Dict[str, Any]:
    # Add new workflow logic
    if workflow_type == "new_workflow":
        return self._execute_new_workflow(parameters)
```

## 📁 Project Structure

```
Major Project BE/
├── backend/                    # Python FastAPI Backend
│   ├── agents/                # AI Agents
│   │   ├── agent_manager.py   # Multi-Agent Coordinator
│   │   ├── whatsapp_agent.py  # WhatsApp Integration
│   │   ├── filesearch_agent.py# File System Operations
│   │   └── conversation_agent.py# Conversational AI
│   ├── utils/                 # Utilities
│   │   └── enhanced_speech_processor.py# Audio Processing
│   ├── config.py              # Configuration Management
│   ├── crew_config.py         # CrewAI Setup
│   ├── crew_main.py          # Enhanced CrewAI Server
│   ├── main.py               # Primary FastAPI Server
│   ├── streamlit_app.py      # Streamlit Interface
│   └── requirements.txt      # Python Dependencies
├── frontend/                  # Next.js Frontend
│   ├── src/
│   │   ├── app/              # App Router Pages
│   │   ├── components/       # UI Components
│   │   └── hooks/            # React Hooks
│   ├── package.json          # Node Dependencies
│   └── tailwind.config.ts    # Styling Configuration
├── test_files/               # Sample Files for Testing
├── setup_enhanced_vaani.bat  # Automated Setup Script
├── start_vaani_backend.bat   # Backend Launcher
└── README_Enhanced_Vaani.md  # Detailed Documentation
```

## 🔮 Future Enhancements

### Phase 2: Advanced Capabilities
- **📞 Call Agent**: Voice call automation
- **📧 Email Agent**: Smart email composition
- **📅 Calendar Agent**: Advanced scheduling
- **🌐 Web Agent**: Intelligent web search

### Phase 3: AI Enhancement
- **🧠 Memory System**: Long-term conversation memory
- **🎯 Personalization**: Learning user preferences
- **🔮 Predictive**: Anticipating user needs
- **🌍 Multi-Language**: Global language support

## 📝 API Reference

### Key Endpoints

- **POST /process-command**: Execute AI commands
- **POST /text-to-speech**: Convert text to speech
- **GET /agents**: List available agents
- **GET /health**: System health check
- **WebSocket /ws**: Real-time communication

### Request/Response Format

```typescript
// Command Request
interface CommandRequest {
  command: string;
  user_id?: string;
}

// Command Response
interface CommandResponse {
  success: boolean;
  message: string;
  intent: string;
  agent_used: string;
  timestamp: string;
  requires_popup?: boolean;
  whatsapp_url?: string;
  file_info?: any;
}
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **CrewAI** for multi-agent orchestration
- **Groq** for lightning-fast LLM inference
- **LangChain** for AI application framework
- **Next.js** for modern React development
- **FastAPI** for high-performance API backend

---

## 🎉 Experience the Future of AI Assistance!

**Vaani** represents the next generation of AI assistants - natural, intelligent, and incredibly capable. Experience the magic of conversational AI with powerful task automation!

```bash
# Start your AI journey today!
setup_enhanced_vaani.bat
```

**Made with ❤️ for the future of human-AI interaction**