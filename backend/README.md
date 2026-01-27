# 🤖 AI Task Automation Assistant

A voice-powered AI assistant that automates daily tasks using natural language commands. Built with **FastAPI**, **Streamlit**, **LangGraph**, and **LangChain** with **Groq LLM** integration.

## 🎯 Project Overview

This is an MVP (Minimum Viable Product) focusing on **WhatsApp automation** as the first agent. The system uses:

- **LangGraph** for stateful agent workflows
- **MCP (Multi-Agent Coordinator)** for routing commands to appropriate agents
- **Voice recognition** for hands-free interaction
- **Text-to-speech** for audio feedback
- **FastAPI** backend for processing commands
- **Streamlit** frontend for user interaction

## 🚀 Features

### Current Features (MVP)
- ✅ **WhatsApp Agent**: Send messages via voice/text commands
- ✅ **Voice Recognition**: Hands-free command input using speech-to-text
- ✅ **Text-to-Speech**: Audio feedback for responses
- ✅ **Contact Search**: Find contacts by name (mock database)
- ✅ **URL Generation**: Create WhatsApp wa.me deep links
- ✅ **Command History**: Track and review past commands
- ✅ **Error Handling**: Graceful error handling and user feedback

### Planned Agents (Future Versions)
- 🔄 **FileSearch Agent**: Find and open files from local storage
- 🔄 **Calendar Agent**: Schedule meetings and manage events
- 🔄 **Call Agent**: Initiate phone calls
- 🔄 **Notes Agent**: Voice note-taking and organization
- 🔄 **Email Agent**: Send and manage emails
- 🔄 **GoogleSearch Agent**: Web search with summarization
- 🔄 **YouTube Agent**: Search and play videos

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Streamlit UI   │    │   FastAPI       │    │   LangGraph     │
│  - Voice Input  │◄──►│   - REST API    │◄──►│   - Workflows   │
│  - Text Input   │    │   - CORS        │    │   - State Mgmt  │
│  - TTS Output   │    │   - Validation  │    │   - Agent Chain │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Speech Processor│    │ Agent Manager   │    │ WhatsApp Agent  │
│ - STT/TTS       │    │ - MCP Router    │    │ - Contact Search│
│ - Audio Devices │    │ - Intent Detect │    │ - URL Generation│
│ - Microphone    │    │ - Agent Coord   │    │ - LangChain     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

- **Python 3.8+**
- **Microphone** (for voice input)
- **Speakers/Headphones** (for audio output)
- **Groq API Key** (for LLM functionality)

## 🛠️ Installation & Setup

### Step 1: Clone and Install Dependencies

```bash
# Clone the repository (or extract files)
cd "Major Project BE"

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment

1. **Update `.env` file** with your Groq API key:

```env
# Replace with your actual Groq API key
GROQ_API_KEY=your_actual_groq_api_key_here

# Other settings (can keep defaults)
GROQ_MODEL=llama3-70b-8192
FASTAPI_HOST=127.0.0.1
FASTAPI_PORT=8000
STREAMLIT_PORT=8501
```

2. **Get Groq API Key**:
   - Visit [Groq Console](https://console.groq.com)
   - Sign up/Login
   - Create an API key
   - Replace `your_actual_groq_api_key_here` in `.env`

### Step 3: Run the Application

#### Option A: Use Batch Scripts (Windows)

```batch
# Setup (first time only)
setup.bat

# Start backend server
start_backend.bat

# In a new terminal, start frontend
start_frontend.bat
```

#### Option B: Manual Commands

```bash
# Terminal 1: Start Backend
python main.py

# Terminal 2: Start Frontend  
streamlit run streamlit_app.py --server.port=8501
```

### Step 4: Test the System

```bash
# Run automated tests
python test_assistant.py
```

## 🎮 Usage Examples

### Voice Commands
1. Click **"🎤 Start Voice Command"** in the Streamlit UI
2. Speak clearly:
   - *"Send WhatsApp to Jay: Hello how are you"*
   - *"Message Mom on WhatsApp: I'll be late today"*
   - *"WhatsApp Vijay: Can we reschedule the meeting?"*

### Text Commands
1. Type in the text input field:
   - `Send WhatsApp to Jay: Hello how are you`
   - `Message Mom on WhatsApp: I'll be late today`
   - `WhatsApp Vijay: Meeting at 5 PM`

### Expected Output
- ✅ **Success**: "WhatsApp message ready for Jay! Click the link to send: https://wa.me/919876543210?text=Hello%20how%20are%20you"
- ❌ **Error**: "Contact 'UnknownPerson' not found in your contacts"

## 📁 Project Structure

```
Major Project BE/
├── agents/
│   ├── __init__.py
│   ├── agent_manager.py      # MCP coordinator
│   └── whatsapp_agent.py     # WhatsApp agent with LangGraph
├── utils/
│   ├── __init__.py
│   └── speech_processor.py   # Voice input/output handling
├── config.py                 # Configuration management
├── main.py                   # FastAPI backend server
├── streamlit_app.py          # Streamlit frontend
├── test_assistant.py         # Automated testing
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
├── setup.bat                 # Setup script
├── start_backend.bat         # Backend startup
├── start_frontend.bat        # Frontend startup
└── README.md                 # This file
```

## 🔧 Configuration

### Environment Variables (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Groq LLM API key | *Required* |
| `GROQ_MODEL` | Groq model to use | `llama3-70b-8192` |
| `FASTAPI_HOST` | Backend host | `127.0.0.1` |
| `FASTAPI_PORT` | Backend port | `8000` |
| `STREAMLIT_PORT` | Frontend port | `8501` |
| `SPEECH_TIMEOUT` | Speech listening timeout | `5` |
| `SPEECH_PHRASE_TIME_LIMIT` | Max phrase duration | `10` |
| `AGENT_TEMPERATURE` | LLM temperature | `0.1` |
| `MAX_RESPONSE_TOKENS` | Max LLM response length | `1000` |

### Mock Contact Database

The WhatsApp agent includes a mock contact database for testing:

```python
mock_contacts = {
    "jay": "+919876543210",
    "vijay": "+919876543211", 
    "mom": "+919876543212",
    "dad": "+919876543213",
    "john": "+919876543214",
    "alice": "+919876543215",
    "boss": "+919876543216"
}
```

## 🧪 Testing

### Automated Tests

```bash
python test_assistant.py
```

Tests include:
- ✅ Backend health and connectivity
- ✅ WhatsApp agent functionality
- ✅ Command parsing and routing
- ✅ Error handling and edge cases
- ✅ Configuration validation

### Manual Testing

1. **Backend Health**: Visit http://127.0.0.1:8000/health
2. **API Documentation**: Visit http://127.0.0.1:8000/docs
3. **Frontend Interface**: Visit http://localhost:8501

### Test Commands

```
✅ "Send WhatsApp to Jay: Hello"
✅ "Message Mom on WhatsApp: I'll be late"
✅ "WhatsApp Vijay: Meeting at 5 PM"
❌ "Send WhatsApp to UnknownContact: Hello" (should fail)
❌ "Call John" (not implemented yet)
❌ "Open file project.pdf" (not implemented yet)
```

## 🚨 Troubleshooting

### Common Issues

1. **"Backend not available"**
   - Check if FastAPI server is running on port 8000
   - Verify GROQ_API_KEY in .env file
   - Run `python test_assistant.py` to diagnose

2. **"Microphone test failed"**
   - Check microphone permissions
   - Ensure microphone is not used by other apps
   - Try different audio input device

3. **"Speech recognition error"**
   - Check internet connection (Google Speech Recognition)
   - Speak clearly and at normal pace
   - Reduce background noise

4. **"GROQ API Error"**
   - Verify API key is correct
   - Check Groq service status
   - Ensure API quota is not exceeded

### Debug Commands

```bash
# Check configuration
python -c "from config import config; config.validate_config()"

# Test backend directly
curl http://127.0.0.1:8000/health

# Check dependencies
pip list | grep -E "(langchain|langgraph|groq|streamlit|fastapi)"
```

## 🛣️ Roadmap

### Phase 1: MVP ✅
- [x] WhatsApp Agent with voice/text input
- [x] LangGraph workflow implementation
- [x] Streamlit frontend with TTS/STT
- [x] Comprehensive testing suite

### Phase 2: File & Communication Agents
- [ ] FileSearch Agent (local file operations)
- [ ] Call Agent (telephony integration)
- [ ] Email Agent (SMTP/IMAP integration)

### Phase 3: Productivity Agents
- [ ] Calendar Agent (Google Calendar API)
- [ ] Notes Agent (advanced note-taking)
- [ ] GoogleSearch Agent (web search)

### Phase 4: Advanced Features
- [ ] User authentication and profiles
- [ ] Multi-language support
- [ ] Mobile app (React Native)
- [ ] Smart home integration

## 📄 API Reference

### FastAPI Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check with system info |
| `/health` | GET | Detailed health status |
| `/process-command` | POST | Process text/voice commands |
| `/agents` | GET | List available agents |
| `/config` | GET | Get system configuration |

### Request/Response Examples

**Process Command:**
```json
POST /process-command
{
  "command": "Send WhatsApp to Jay: Hello how are you"
}

Response:
{
  "success": true,
  "message": "✅ WhatsApp message ready for Jay! Click the link to send: https://wa.me/919876543210?text=Hello%20how%20are%20you",
  "intent": "whatsapp",
  "agent_used": "whatsapp",
  "timestamp": "2024-08-24T10:30:00",
  "details": {
    "original_command": "Send WhatsApp to Jay: Hello how are you",
    "agent_response": {
      "whatsapp_url": "https://wa.me/919876543210?text=Hello%20how%20are%20you"
    }
  }
}
```

## 🤝 Contributing

### Adding New Agents

1. **Create Agent File**: `agents/new_agent.py`
2. **Implement LangGraph Workflow**: Use StateGraph for stateful operations
3. **Register in Agent Manager**: Add to `agents/agent_manager.py`
4. **Update Intent Detection**: Modify intent classification
5. **Add Tests**: Include in `test_assistant.py`

### Example Agent Template

```python
from langgraph.graph import StateGraph, END
from pydantic import BaseModel

class NewAgentState(BaseModel):
    user_input: str
    result: str = ""
    error: str = ""

class NewAgent:
    def __init__(self):
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        workflow = StateGraph(NewAgentState)
        # Add nodes and edges
        return workflow.compile()
    
    def process_command(self, user_input: str) -> dict:
        # Implementation
        pass
```

## 📞 Support

For issues and questions:
1. Check this README and troubleshooting section
2. Run automated tests: `python test_assistant.py`
3. Check logs in terminal outputs
4. Verify configuration with `config.validate_config()`

## 📜 License

This project is developed as a final year major project for educational purposes.

---

## 🎉 Quick Start Summary

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Update .env with your Groq API key
# GROQ_API_KEY=your_actual_groq_api_key_here

# 3. Start backend
python main.py

# 4. Start frontend (new terminal)
streamlit run streamlit_app.py --server.port=8501

# 5. Test the system
python test_assistant.py

# 6. Try voice command: "Send WhatsApp to Jay: Hello!"
```

**🎯 Your AI Assistant is ready! Visit http://localhost:8501 to start automating tasks with voice commands!**