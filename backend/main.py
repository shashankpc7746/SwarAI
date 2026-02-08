"""
FastAPI Backend for AI Task Automation Assistant
Main server handling voice/text commands and agent coordination
"""

from fastapi import FastAPI, HTTPException, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, Set
import uvicorn
import logging
import json
import asyncio
from datetime import datetime

from config import config
from agents.agent_manager import agent_manager
from utils.enhanced_speech_processor import enhanced_speech_processor
from auth import auth_router

# JSON serialization helper function
def json_serializable(obj):
    """Convert objects to JSON serializable format"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [json_serializable(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        return json_serializable(obj.__dict__)
    else:
        return obj

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Task Automation Assistant",
    description="Voice-powered AI assistant for automating daily tasks",
    version="1.0.0"
)

# Add CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],  # Allow Next.js dev server and all origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include authentication router
app.include_router(auth_router)

# Startup message with enhanced features
@app.on_event("startup")
async def startup_event():
    """Initialize application with enhanced features"""
    logger.info("🚀 Starting Enhanced AI Task Automation Assistant (SwarAI)...")
    logger.info("✨ Features: Conversational AI, FileSearch, Multi-Agent Coordination")
    
    # Validate configuration
    if not config.validate_config():
        logger.warning("⚠️  Configuration validation failed. Some features may not work.")
    
    logger.info("✅ SwarAI AI Assistant started successfully!")
    logger.info("🤖 Available agents: WhatsApp, FileSearch, Conversation")
    logger.info("🎯 Enhanced NLP and multi-agent workflows ready!")

# Pydantic models for request/response
class CommandRequest(BaseModel):
    """Request model for text commands"""
    command: str
    user_id: Optional[str] = "default_user"

class CommandResponse(BaseModel):
    """Response model for processed commands"""
    success: bool
    message: str
    intent: str
    agent_used: str
    timestamp: str
    details: Optional[Dict[str, Any]] = None

class TTSRequest(BaseModel):
    """Request model for text-to-speech"""
    text: str
    language: Optional[str] = "en"

class TTSResponse(BaseModel):
    """Response model for text-to-speech"""
    success: bool
    message: str
    timestamp: str

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str
    agents_available: list

# @app.on_startup
# async def startup_event():
#     """Initialize application on startup"""
#     logger.info("🚀 Starting AI Task Automation Assistant...")
    
#     # Validate configuration
#     if not config.validate_config():
#         logger.warning("⚠️  Configuration validation failed. Some features may not work.")
    
#     logger.info("✅ AI Task Automation Assistant started successfully!")

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with enhanced health check"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="2.0.0 - Enhanced with SwarAI AI",
        agents_available=agent_manager.get_available_agents()
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Enhanced health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="2.0.0 - Enhanced with SwarAI AI",
        agents_available=agent_manager.get_available_agents()
    )

@app.post("/process-command", response_model=CommandResponse)
async def process_command(request: CommandRequest):
    """
    Process text or voice-to-text commands through enhanced MCP agent manager
    Now with conversational AI, FileSearch, and multi-agent coordination
    """
    try:
        logger.info(f"Processing command: {request.command}")
        
        if not request.command or not request.command.strip():
            raise HTTPException(status_code=400, detail="Command cannot be empty")
        
        # Process command through enhanced agent manager with timeout
        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(agent_manager.process_command, request.command),
                timeout=30.0  # 30 second timeout
            )
        except asyncio.TimeoutError:
            logger.error(f"Command processing timeout: {request.command}")
            raise HTTPException(status_code=504, detail="Command processing timeout. Please try a more specific query.")
        
        # Enhanced logging with agent information
        logger.info(f"Command processed - Success: {result['success']}, Agent: {result['agent_used']}, Intent: {result['intent']}")
        
        # Safe extraction of agent response
        agent_response = result.get('agent_response', {})
        if agent_response is None:
            agent_response = {}
        
        # Enhanced response structure with safe access
        response = CommandResponse(
            success=result["success"],
            message=result["message"],
            intent=result["intent"],
            agent_used=result["agent_used"],
            timestamp=datetime.now().isoformat(),
            details={
                "original_command": request.command,
                "agent_response": agent_response,
                "error": result.get("error"),
                "workflow": result.get("workflow"),
                "conversation_context": result.get("conversation_context"),
                "file_results": agent_response.get("search_results", []),
                "selected_file": agent_response.get("selected_file"),
                "action_type": agent_response.get("action_type"),
                "whatsapp_url": result.get("whatsapp_url") or agent_response.get("whatsapp_url")
            }
        )
        
        logger.info(f"Response prepared successfully for command: {request.command}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing command: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/process-voice")
async def process_voice(audio_file: UploadFile = File(...)):
    """
    Process voice commands (placeholder for future implementation)
    Currently returns a message directing to use text commands
    """
    try:
        logger.info(f"Voice file received: {audio_file.filename}")
        
        # For MVP, we'll direct users to use text commands
        # In future versions, this will handle speech-to-text conversion
        
        return JSONResponse(
            content={
                "success": False,
                "message": "🎤 Voice processing is not yet implemented in the backend. Please use text commands for now. Try: 'Send WhatsApp to Jay: Hello!'",
                "intent": "voice_not_implemented",
                "agent_used": "none",
                "timestamp": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing voice: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Voice processing error: {str(e)}")

@app.post("/text-to-speech", response_model=TTSResponse)
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech using SwarAI's enhanced TTS system
    Provides audio feedback for responses
    """
    try:
        logger.info(f"TTS request: {request.text[:50]}...")
        
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Use enhanced speech processor for TTS
        success = enhanced_speech_processor.text_to_speech_enhanced(
            text=request.text,
            language=request.language
        )
        
        return TTSResponse(
            success=success,
            message=f"Audio played: {request.text[:50]}..." if success else "Audio playback failed",
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in TTS: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")

@app.get("/agents")
async def get_agents():
    """Get list of available agents with enhanced information"""
    try:
        agents = agent_manager.get_available_agents()
        agent_info = {
            "whatsapp": {
                "name": "WhatsApp Agent",
                "description": "Send messages via WhatsApp with natural language",
                "capabilities": ["Send messages", "Contact search", "URL generation"],
                "examples": ["Send WhatsApp to Mom: I'm coming home", "Tell dad about the meeting"]
            },
            "email": {
                "name": "Email Agent",
                "description": "Compose and send emails via default mail client",
                "capabilities": ["Email composition", "Send emails", "Draft emails"],
                "examples": ["Email boss about the meeting", "Send email to john with subject Project Update"]
            },
            "calendar": {
                "name": "Calendar Agent",
                "description": "Schedule meetings and events",
                "capabilities": ["Create events", "Schedule meetings", "Set appointments"],
                "examples": ["Schedule meeting tomorrow at 3pm", "Create event for Monday morning"]
            },
            "phone": {
                "name": "Phone Agent",
                "description": "Make phone calls via system dialer",
                "capabilities": ["Call contacts", "Dial numbers", "Contact search"],
                "examples": ["Call mom", "Phone vijay", "Dial +1234567890"]
            },
            "payment": {
                "name": "Payment Agent",
                "description": "Send payments via various apps (PayPal, Google Pay, etc.)",
                "capabilities": ["PayPal payments", "UPI payments", "Send money"],
                "examples": ["Pay $50 to john via paypal", "Send 100 rupees to vijay via paytm"]
            },
            "app_launcher": {
                "name": "App Launcher Agent",
                "description": "Open applications and programs on your device",
                "capabilities": ["Launch apps", "Open programs", "Start browsers"],
                "examples": ["Open chrome", "Launch calculator", "Start notepad"]
            },
            "websearch": {
                "name": "Web Search Agent",
                "description": "Perform web searches on Google, YouTube, etc.",
                "capabilities": ["Google search", "YouTube search", "Web browsing"],
                "examples": ["Search for python tutorials", "Google best restaurants near me"]
            },
            "task": {
                "name": "Task Management Agent",
                "description": "Manage tasks, to-do lists, and reminders",
                "capabilities": ["Add tasks", "List tasks", "Complete tasks", "Set reminders"],
                "examples": ["Add task buy groceries", "List my tasks", "Remind me to call mom tomorrow"]
            },
            "conversation": {
                "name": "SwarAI (Conversational AI)",
                "description": "Natural conversation and assistance",
                "capabilities": ["Greetings", "Help guidance", "Natural chat", "Task clarification"],
                "examples": ["Hello", "What can you do?", "Help me", "Thank you"]
            },
            "filesearch": {
                "name": "FileSearch Agent",
                "description": "Find, open, and share files across devices",
                "capabilities": ["File search", "File opening", "Cross-platform support", "File sharing prep"],
                "examples": ["Find my report", "Open presentation.pptx", "Search for photos"]
            }
        }
        
        return {
            "success": True,
            "agents": agents,
            "agent_details": agent_info,
            "count": len(agents),
            "multi_agent_support": True,
            "natural_language": True,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting agents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config")
async def get_config():
    """Get application configuration (non-sensitive info only)"""
    try:
        return {
            "success": True,
            "config": {
                "groq_model": config.GROQ_MODEL,
                "fastapi_host": config.FASTAPI_HOST,
                "fastapi_port": config.FASTAPI_PORT,
                "agent_temperature": config.AGENT_TEMPERATURE,
                "max_response_tokens": config.MAX_RESPONSE_TOKENS,
                "agents_available": agent_manager.get_available_agents()
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket Manager for real-time communication
class WebSocketManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"🔌 WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"🔌 WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_message(self, websocket: WebSocket, message: dict):
        try:
            # Convert message to JSON serializable format
            serializable_message = json_serializable(message)
            await websocket.send_text(json.dumps(serializable_message))
        except Exception as e:
            logger.error(f"❌ Error sending WebSocket message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: dict):
        disconnected = set()
        # Convert message to JSON serializable format
        serializable_message = json_serializable(message)
        message_text = json.dumps(serializable_message)
        
        for connection in self.active_connections.copy():
            try:
                await connection.send_text(message_text)
            except Exception:
                disconnected.add(connection)
        
        for conn in disconnected:
            self.disconnect(conn)

# Initialize WebSocket manager
ws_manager = WebSocketManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await ws_manager.send_message(websocket, {
                    "type": "pong", 
                    "timestamp": datetime.now().isoformat()
                })
            
            elif message.get("type") == "command":
                command = message.get("command", "")
                if command:
                    # Process command using the real agent manager
                    request = CommandRequest(command=command)
                    result = await process_command(request)
                    
                    # Convert result to WebSocket format
                    await ws_manager.send_message(websocket, {
                        "type": "command_result",
                        "data": {
                            "success": result.success,
                            "message": result.message,
                            "intent": result.intent,
                            "agent_used": result.agent_used,
                            "timestamp": result.timestamp,
                            "crew_used": result.agent_used,  # For frontend compatibility
                            "agents_involved": [result.agent_used],
                            "execution_time": 0,
                            "workflow_id": "ws_" + datetime.now().strftime("%Y%m%d_%H%M%S"),
                            "results": result.details or {}
                        }
                    })
    
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        ws_manager.disconnect(websocket)

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "message": "Endpoint not found",
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    # Validate configuration before starting
    if not config.validate_config():
        logger.error("❌ Configuration validation failed. Please check your .env file.")
        exit(1)
    
    # Use port 8000 for Next.js frontend integration
    HOST = "0.0.0.0"
    PORT = 8000
    
    logger.info(f"🚀 Starting FastAPI server on {HOST}:{PORT}")
    logger.info(f"📡 API will be available at: http://localhost:{PORT}")
    logger.info(f"🌐 Next.js frontend should connect to: http://localhost:{PORT}")
    
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=True,
        log_level="info"
    )