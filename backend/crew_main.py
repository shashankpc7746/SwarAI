"""
CrewAI Multi-Agent Backend Server
Enhanced with Real Functionality: Voice Recognition, File Access, and Agent Coordination
"""

import os
import logging
import json
import glob
import platform
import subprocess
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional, Set
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

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

# Import real functionality from main.py components
try:
    from config import config
    CONFIG_AVAILABLE = True
except ImportError:
    config = None
    CONFIG_AVAILABLE = False
    print("⚠️  Configuration not available")

try:
    from agents.agent_manager import agent_manager
    AGENT_MANAGER_AVAILABLE = True
except Exception as e:
    agent_manager = None
    AGENT_MANAGER_AVAILABLE = False
    print(f"⚠️  Agent Manager not available: {e}")

try:
    from utils.enhanced_speech_processor import enhanced_speech_processor
    SPEECH_PROCESSOR_AVAILABLE = True
except Exception as e:
    enhanced_speech_processor = None
    SPEECH_PROCESSOR_AVAILABLE = False
    print(f"⚠️  Enhanced Speech Processor not available: {e}")

try:
    from utils.conversational_tts import conversational_tts
    from utils.conversation_memory import conversation_memory
    CONVERSATIONAL_AI_AVAILABLE = True
except Exception as e:
    conversational_tts = None
    conversation_memory = None
    CONVERSATIONAL_AI_AVAILABLE = False
    print(f"⚠️  Conversational AI features not available: {e}")

# Import CrewAI orchestrator
try:
    from crew_config import orchestrator
    CREWAI_AVAILABLE = True
except ImportError:
    orchestrator = None
    CREWAI_AVAILABLE = False
    print("⚠️  CrewAI not available, using fallback mode")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enhanced Request/Response Models from main.py
class CommandRequest(BaseModel):
    """Enhanced request model for text commands"""
    command: str = Field(..., min_length=1, max_length=1000)
    user_id: Optional[str] = "default_user"

class CommandResponse(BaseModel):
    """Enhanced response model for processed commands"""
    success: bool
    message: str
    intent: str
    agent_used: str
    timestamp: str
    requires_popup: bool = False
    whatsapp_url: Optional[str] = None
    file_info: Optional[Dict] = None
    details: Optional[Dict[str, Any]] = None

class TTSRequest(BaseModel):
    """Request model for text-to-speech"""
    text: str
    language: Optional[str] = "en"
    voice_speed: Optional[float] = 1.0

class TTSResponse(BaseModel):
    """Response model for text-to-speech"""
    success: bool
    message: str
    timestamp: str

class HealthResponse(BaseModel):
    """Enhanced health check response"""
    status: str
    timestamp: str
    version: str
    agents_available: list
    crewai_available: bool
    speech_available: bool
    config_available: bool

# Enhanced File Manager with Real File System Access
class EnhancedFileManager:
    """Enhanced file manager with real file system access"""
    
    def __init__(self):
        self.search_locations = self._get_search_locations()
    
    def search_files(self, query: str, file_types: List[str] = None) -> List[Dict]:
        """Search for files with enhanced patterns and real file access"""
        try:
            results = []
            query = query.lower().strip()
            
            # Enhanced search patterns
            patterns = [
                f"*{query}*",
                f"*{query}*.*",
                f"{query}*",
                f"*{query}"
            ]
            
            # Add file type specific patterns
            if file_types:
                for file_type in file_types:
                    patterns.extend([
                        f"*{query}*.{file_type}",
                        f"{query}*.{file_type}"
                    ])
            
            for location in self.search_locations:
                try:
                    for pattern in patterns:
                        matches = glob.glob(os.path.join(location, '**', pattern), recursive=True)
                        
                        for match in matches[:10]:  # Limit to 10 per location
                            if os.path.isfile(match):
                                file_info = {
                                    'name': os.path.basename(match),
                                    'path': match,
                                    'size': os.path.getsize(match),
                                    'modified': datetime.fromtimestamp(os.path.getmtime(match)).isoformat(),
                                    'extension': os.path.splitext(match)[1],
                                    'location': os.path.dirname(match)
                                }
                                
                                # Avoid duplicates
                                if not any(r['path'] == file_info['path'] for r in results):
                                    results.append(file_info)
                except Exception as e:
                    logger.warning(f"Search error in {location}: {e}")
                    continue
            
            # Sort by relevance (name match first, then modified date)
            results.sort(key=lambda x: (
                not query in x['name'].lower(),
                -os.path.getmtime(x['path'])
            ))
            
            return results[:15]  # Return top 15 results
            
        except Exception as e:
            logger.error(f"File search error: {e}")
            return []
    
    def _get_search_locations(self) -> List[str]:
        """Get enhanced search locations based on platform"""
        locations = []
        
        if platform.system().lower() == "windows":
            user_profile = os.environ.get('USERPROFILE', '')
            potential_locations = [
                os.path.join(user_profile, 'Documents'),
                os.path.join(user_profile, 'Desktop'),
                os.path.join(user_profile, 'Downloads'),
                os.path.join(user_profile, 'Pictures'),
                os.path.join(user_profile, 'Videos'),
                os.path.join(user_profile, 'OneDrive'),
                'C:\\Users\\Public\\Documents'
            ]
        else:
            # Linux/Mac support
            home = os.path.expanduser('~')
            potential_locations = [
                os.path.join(home, 'Documents'),
                os.path.join(home, 'Desktop'),
                os.path.join(home, 'Downloads'),
                os.path.join(home, 'Pictures'),
                os.path.join(home, 'Videos')
            ]
        
        # Only include existing locations
        for loc in potential_locations:
            if os.path.exists(loc):
                locations.append(loc)
        
        return locations
    
    def open_file(self, file_path: str) -> Dict[str, Any]:
        """Open file with enhanced error handling and platform support"""
        try:
            if not os.path.exists(file_path):
                return {'success': False, 'error': 'File not found'}
            
            system = platform.system().lower()
            
            if system == "windows":
                os.startfile(file_path)
            elif system == "darwin":  # macOS
                subprocess.run(["open", file_path])
            else:  # Linux
                subprocess.run(["xdg-open", file_path])
            
            return {
                'success': True,
                'message': f'Opened {os.path.basename(file_path)}',
                'file_info': {
                    'name': os.path.basename(file_path),
                    'path': file_path,
                    'size': os.path.getsize(file_path)
                }
            }
            
        except Exception as e:
            logger.error(f"Error opening file {file_path}: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get detailed file information"""
        try:
            if not os.path.exists(file_path):
                return {'success': False, 'error': 'File not found'}
            
            stat = os.stat(file_path)
            return {
                'success': True,
                'name': os.path.basename(file_path),
                'path': file_path,
                'size': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'extension': os.path.splitext(file_path)[1],
                'is_file': os.path.isfile(file_path),
                'is_directory': os.path.isdir(file_path)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Enhanced WhatsApp Manager with Real Contact Management
class EnhancedWhatsAppManager:
    """Enhanced WhatsApp manager with better contact handling and URL generation"""
    
    def __init__(self):
        # Enhanced contact database with more realistic contacts
        self.contacts = {
            "jay": "+919876543210",
            "mom": "+919876543211", 
            "dad": "+919876543212",
            "friend": "+919876543213",
            "colleague": "+919876543214",
            "boss": "+919876543215",
            "brother": "+919876543216",
            "sister": "+919876543217",
            "wife": "+919876543218",
            "husband": "+919876543219"
        }
    
    def find_contact(self, contact_name: str) -> Optional[str]:
        """Find contact with fuzzy matching"""
        contact_name = contact_name.lower().strip()
        
        # Exact match first
        if contact_name in self.contacts:
            return self.contacts[contact_name]
        
        # Fuzzy matching
        for name, phone in self.contacts.items():
            if contact_name in name or name in contact_name:
                return phone
        
        # Return default if no match
        return "+919876543210"  # Default to Jay
    
    def create_link(self, contact: str, message: str, file_info: Dict = None) -> str:
        """Create enhanced WhatsApp link with proper encoding"""
        phone = self.find_contact(contact)
        
        # Enhanced message formatting
        if file_info:
            size_mb = file_info.get('size', 0) / (1024 * 1024)
            text = f"📎 Sharing file: *{file_info['name']}* ({size_mb:.1f}MB)\n\n{message}"
        else:
            text = message
        
        # Proper URL encoding
        import urllib.parse
        encoded_phone = urllib.parse.quote(phone.replace("+", ""))
        encoded_text = urllib.parse.quote(text)
        
        # Use the format specified in project requirements
        return f"https://api.whatsapp.com/send/?phone=%2B{encoded_phone}&text={encoded_text}&type=phone_number&app_absent=0"
    
    def get_contact_list(self) -> Dict[str, str]:
        """Get list of available contacts"""
        return self.contacts.copy()
    
    def add_contact(self, name: str, phone: str) -> bool:
        """Add new contact to the database"""
        try:
            self.contacts[name.lower()] = phone
            return True
        except Exception:
            return False

# Initialize enhanced managers
file_manager = EnhancedFileManager()
whatsapp_manager = EnhancedWhatsAppManager()

# Enhanced startup function
async def startup_logic():
    """Initialize application with enhanced features"""
    logger.info("🚀 Starting Enhanced CrewAI Multi-Agent Backend...")
    logger.info("✨ Features: CrewAI Orchestration + Real Voice + File Access + Agent Coordination")
    
    # Validate configuration
    if CONFIG_AVAILABLE and config:
        if not config.validate_config():
            logger.warning("⚠️  Configuration validation failed. Some features may not work.")
        else:
            logger.info("✅ Configuration validated successfully!")
    
    logger.info(f"✅ Enhanced CrewAI Assistant started successfully!")
    logger.info(f"🤖 CrewAI Available: {CREWAI_AVAILABLE}")
    logger.info(f"🎤 Speech Processing Available: {SPEECH_PROCESSOR_AVAILABLE}")
    logger.info(f"📁 Enhanced File Manager: Enabled")
    logger.info(f"📱 Enhanced WhatsApp Manager: Enabled")
    logger.info(f"🎯 Real Agent Coordination: {AGENT_MANAGER_AVAILABLE}")

# Enhanced FastAPI app with lifespan management
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await startup_logic()
    yield
    # Shutdown (if needed)
    logger.info("🔴 Shutting down Enhanced CrewAI Backend...")

app = FastAPI(
    title="CrewAI Multi-Agent Backend with Enhanced Functionality", 
    description="Advanced AI assistant with voice recognition, file management, and CrewAI orchestration",
    version="3.0.0",
    lifespan=lifespan
)

# Enhanced CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Note: Using modern lifespan management instead of deprecated startup events

@app.get("/", response_model=HealthResponse)
async def root():
    """Enhanced root endpoint with comprehensive system status"""
    agents_available = []
    if AGENT_MANAGER_AVAILABLE and agent_manager:
        agents_available = agent_manager.get_available_agents()
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="3.0.0 - Enhanced CrewAI with Real Functionality",
        agents_available=agents_available,
        crewai_available=CREWAI_AVAILABLE,
        speech_available=SPEECH_PROCESSOR_AVAILABLE,
        config_available=CONFIG_AVAILABLE
    )

@app.get("/health", response_model=HealthResponse)
async def health():
    """Enhanced health check with detailed component status"""
    agents_available = []
    if AGENT_MANAGER_AVAILABLE and agent_manager:
        agents_available = agent_manager.get_available_agents()
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="3.0.0 - Enhanced CrewAI with Real Functionality",
        agents_available=agents_available,
        crewai_available=CREWAI_AVAILABLE,
        speech_available=SPEECH_PROCESSOR_AVAILABLE,
        config_available=CONFIG_AVAILABLE
    )

@app.post("/process-command", response_model=CommandResponse)
async def process_command(request: CommandRequest) -> CommandResponse:
    """Enhanced command processing with natural conversation and voice feedback"""
    logger.info(f"📥 Processing conversational command: {request.command}")
    
    # Special handling for frontend fallback requests to prevent infinite loops
    command = request.command.strip()
    if command.lower().startswith(('open whatsapp link from:', 'extract whatsapp link from:')):
        logger.info("⚠️ Detected frontend fallback request - providing safe response")
        return CommandResponse(
            success=False,
            message="❌ No valid WhatsApp link found in the provided content. Please try a direct WhatsApp command like 'Send WhatsApp to [contact]: [message]'.",
            intent="whatsapp_extraction_failed",
            agent_used="fallback_handler",
            timestamp=datetime.now().isoformat(),
            requires_popup=False,
            details={"original_command": command, "processing_method": "fallback_prevention"}
        )
    
    try:
        # Validate input
        if not command:
            raise HTTPException(status_code=400, detail="Command cannot be empty")
        user_id = request.user_id or "default_user"
        
        # Get conversation context for better responses
        conversation_context = None
        if CONVERSATIONAL_AI_AVAILABLE and conversation_memory:
            conversation_context = await conversation_memory.get_conversation_context(user_id)
        
        # Try real agent manager first (preferred)
        if AGENT_MANAGER_AVAILABLE and agent_manager:
            logger.info("🎯 Using real agent manager with conversational AI")
            
            result = agent_manager.process_command(command)
            
            # Enhanced logging
            logger.info(f"Real agent processed - Success: {result['success']}, Agent: {result['agent_used']}, Intent: {result['intent']}")
            
            # Natural voice feedback (async to not block response)
            if CONVERSATIONAL_AI_AVAILABLE and conversational_tts and config.ENABLE_VOICE_FEEDBACK:
                try:
                    # Create natural response for TTS
                    tts_message = result["message"]
                    
                    # Make it more conversational
                    if result["success"]:
                        if "whatsapp" in result["agent_used"].lower():
                            tts_message = "Perfect! I've prepared your WhatsApp message. Opening it now."
                        elif "filesearch" in result["agent_used"].lower():
                            tts_message = "Great! I found what you're looking for."
                        elif "conversation" in result["agent_used"].lower():
                            tts_message = result["message"]  # Keep conversational responses as-is
                    
                    # Speak asynchronously
                    conversational_tts.speak_threaded(tts_message)
                except Exception as e:
                    logger.warning(f"Voice feedback error: {e}")
            
            # Store conversation in memory
            if CONVERSATIONAL_AI_AVAILABLE and conversation_memory:
                try:
                    await conversation_memory.add_conversation_entry(
                        user_id=user_id,
                        user_message=command,
                        vaani_response=result["message"],
                        metadata={
                            "agent_used": result["agent_used"],
                            "success": result["success"],
                            "intent": result["intent"],
                            "type": "command_execution",
                            "response_time": 0  # Could measure actual time
                        }
                    )
                except Exception as e:
                    logger.warning(f"Memory storage error: {e}")
            
            # Convert to enhanced response format
            return CommandResponse(
                success=result["success"],
                message=result["message"],
                intent=result["intent"],
                agent_used=result["agent_used"],
                timestamp=datetime.now().isoformat(),
                requires_popup="whatsapp" in result["agent_used"].lower() and result["success"],
                whatsapp_url=result.get("whatsapp_url") or result.get("agent_response", {}).get("whatsapp_url"),
                file_info=result.get("agent_response", {}).get("selected_file"),
                details={
                    "original_command": command,
                    "agent_response": result.get("agent_response", {}),
                    "workflow": result.get("workflow"),
                    "conversation_context": conversation_context,
                    "file_results": result.get("agent_response", {}).get("search_results", []),
                    "action_type": result.get("agent_response", {}).get("action_type"),
                    "processing_method": "enhanced_conversational_agent"
                }
            )
        
        # Fallback to CrewAI if available
        elif CREWAI_AVAILABLE and orchestrator:
            logger.info("🤖 Using CrewAI orchestration")
            
            result = orchestrator.execute_workflow(command)
            
            # Extract WhatsApp URL if present
            whatsapp_url = None
            if "wa.me" in result.get('result', '') or "whatsapp.com" in result.get('result', ''):
                import re
                urls = re.findall(r'https://[^\s]+(?:wa\.me|whatsapp\.com)[^\s]*', result.get('result', ''))
                if urls:
                    whatsapp_url = urls[0]
            
            return CommandResponse(
                success=result['success'],
                message=result['result'],
                intent=result.get('workflow_type', 'unknown'),
                agent_used=', '.join(result.get('agents_used', [])),
                timestamp=datetime.now().isoformat(),
                requires_popup=result.get('requires_popup', False),
                whatsapp_url=whatsapp_url,
                details={"processing_method": "crewai_orchestration", "crew_result": result}
            )
        
        # Enhanced fallback processing with real file and WhatsApp managers
        else:
            logger.info("🔧 Using enhanced fallback processing")
            return await process_enhanced_fallback(command)
            
    except Exception as e:
        logger.error(f"❌ Enhanced processing error: {e}")
        return CommandResponse(
            success=False,
            message=f"❌ Error: {str(e)}",
            intent="error",
            agent_used="system",
            timestamp=datetime.now().isoformat(),
            requires_popup=False,
            details={"error": str(e), "processing_method": "error_handler"}
        )

async def process_enhanced_fallback(command: str) -> CommandResponse:
    """Enhanced fallback command processing with real functionality"""
    cmd_lower = command.lower()
    
    # Enhanced pattern matching
    sharing_keywords = ['send', 'share', 'whatsapp', 'message', 'text', 'wa.me']
    file_keywords = ['file', 'document', 'doc', 'pdf', 'photo', 'image', 'video', 'find', 'open', 'search']
    
    has_sharing = any(keyword in cmd_lower for keyword in sharing_keywords)
    has_file = any(keyword in cmd_lower for keyword in file_keywords)
    
    # File + WhatsApp sharing workflow
    if has_file and has_sharing:
        logger.info("📁📱 Processing file + WhatsApp sharing workflow")
        
        # Enhanced file query extraction
        words = command.split()
        file_query = ""
        contact = "jay"  # default
        
        # Smart extraction of file query and contact
        for i, word in enumerate(words):
            if word.lower() in ['send', 'share'] and i + 1 < len(words):
                # Look for file query after send/share
                next_words = words[i+1:i+4]  # Get next few words
                file_query = ' '.join([w for w in next_words if w.lower() not in ['to', 'on', 'via', 'whatsapp']])
            
            # Extract contact name
            word_lower = word.lower()
            if word_lower in whatsapp_manager.get_contact_list():
                contact = word_lower
        
        # If no specific file mentioned, search for common document types
        if not file_query:
            file_query = "document"
        
        # Enhanced file search
        files = file_manager.search_files(file_query, ['pdf', 'doc', 'docx', 'txt', 'jpg', 'png'])
        
        if files:
            file_info = files[0]  # Take the best match
            message = f"Here's the {file_info['name']} file you requested."
            whatsapp_url = whatsapp_manager.create_link(contact, message, file_info)
            
            return CommandResponse(
                success=True,
                message=f"✅ Found '{file_info['name']}' and prepared WhatsApp message for {contact}!\n\n📁 File: {file_info['name']} ({file_info.get('size', 0)/1024/1024:.1f}MB)\n📱 Ready to share on WhatsApp\n📍 Location: {file_info.get('location', 'Unknown')}",
                intent="file_and_share",
                agent_used="enhanced_file_manager, enhanced_whatsapp_agent",
                timestamp=datetime.now().isoformat(),
                requires_popup=True,
                whatsapp_url=whatsapp_url,
                file_info=file_info,
                details={
                    "search_query": file_query,
                    "contact": contact,
                    "files_found": len(files),
                    "processing_method": "enhanced_fallback"
                }
            )
        else:
            return CommandResponse(
                success=False,
                message=f"❌ Could not find file matching '{file_query}'. Try being more specific or check if the file exists.",
                intent="file_search_failed",
                agent_used="enhanced_file_manager",
                timestamp=datetime.now().isoformat(),
                requires_popup=False,
                details={"search_query": file_query, "files_found": 0}
            )
    
    # File operations only
    elif has_file:
        logger.info("📁 Processing file operation")
        
        # Enhanced file query extraction
        words = command.split()
        file_query = ' '.join([w for w in words if w.lower() not in ['find', 'open', 'search', 'file', 'my']])
        
        if not file_query.strip():
            file_query = "document"
        
        files = file_manager.search_files(file_query)
        
        if files:
            file_info = files[0]
            
            # Try to open the file
            open_result = file_manager.open_file(file_info['path'])
            
            if open_result['success']:
                return CommandResponse(
                    success=True,
                    message=f"✅ Found and opened '{file_info['name']}'!\n\n📁 File: {file_info['name']}\n📍 Path: {file_info['path']}\n📅 Modified: {file_info.get('modified', 'Unknown')}\n💾 Size: {file_info.get('size', 0)/1024/1024:.1f}MB",
                    intent="file_operation",
                    agent_used="enhanced_file_manager",
                    timestamp=datetime.now().isoformat(),
                    requires_popup=False,
                    file_info=file_info,
                    details={
                        "action": "open",
                        "search_query": file_query,
                        "files_found": len(files)
                    }
                )
            else:
                return CommandResponse(
                    success=False,
                    message=f"📁 Found '{file_info['name']}' but couldn't open it: {open_result.get('error', 'Unknown error')}",
                    intent="file_open_failed",
                    agent_used="enhanced_file_manager",
                    timestamp=datetime.now().isoformat(),
                    requires_popup=False,
                    file_info=file_info
                )
        else:
            return CommandResponse(
                success=False,
                message=f"❌ Could not find file matching '{file_query}'. Available search locations: {', '.join(file_manager.search_locations[:3])}",
                intent="file_search_failed",
                agent_used="enhanced_file_manager",
                timestamp=datetime.now().isoformat(),
                requires_popup=False,
                details={"search_query": file_query, "search_locations": file_manager.search_locations}
            )
    
    # WhatsApp only
    elif has_sharing:
        logger.info("📱 Processing WhatsApp message")
        
        # Extract contact and message
        words = command.split()
        contact = "jay"
        message = "Hello! This is a message from your AI assistant."
        
        # Try to extract contact
        for word in words:
            if word.lower() in whatsapp_manager.get_contact_list():
                contact = word.lower()
                break
        
        # Extract message content
        if ':' in command:
            message_part = command.split(':', 1)[1].strip()
            if message_part:
                message = message_part
        
        whatsapp_url = whatsapp_manager.create_link(contact, message)
        
        return CommandResponse(
            success=True,
            message=f"✅ WhatsApp message prepared for {contact}!\n\n📱 Contact: {contact} ({whatsapp_manager.find_contact(contact)})\n💬 Message: {message}\n🔗 Ready to send",
            intent="whatsapp_message",
            agent_used="enhanced_whatsapp_agent",
            timestamp=datetime.now().isoformat(),
            requires_popup=True,
            whatsapp_url=whatsapp_url,
            details={"contact": contact, "message": message}
        )
    
    # General help and conversation
    else:
        logger.info("🤖 Processing general help request")
        return CommandResponse(
            success=True,
            message="✅ Enhanced AI Assistant ready! I can help you with:\n\n📁 **File Operations:**\n• 'Find my documents' or 'Open presentation.pptx'\n• Search across Documents, Desktop, Downloads, Pictures\n\n📱 **WhatsApp Messaging:**\n• 'Send message to mom: Hello!'\n• 'Share report.pdf with colleague on WhatsApp'\n\n🤖 **Smart Features:**\n• Real file system access\n• Enhanced contact management\n• Natural language understanding\n• Voice recognition support (when available)",
            intent="general_help",
            agent_used="enhanced_assistant",
            timestamp=datetime.now().isoformat(),
            requires_popup=False,
            details={
                "available_contacts": list(whatsapp_manager.get_contact_list().keys()),
                "search_locations": file_manager.search_locations,
                "features": ["file_search", "whatsapp_messaging", "voice_recognition", "natural_language"]
            }
        )

@app.post("/text-to-speech", response_model=TTSResponse)
async def text_to_speech(request: TTSRequest):
    """Enhanced text-to-speech with real speech processor integration"""
    try:
        logger.info(f"🔊 TTS request: {request.text[:50]}...")
        
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Use enhanced speech processor if available
        if SPEECH_PROCESSOR_AVAILABLE and enhanced_speech_processor:
            success = enhanced_speech_processor.text_to_speech_enhanced(
                text=request.text,
                language=request.language
            )
            
            return TTSResponse(
                success=success,
                message=f"🔊 Audio played: {request.text[:50]}..." if success else "Audio playback failed",
                timestamp=datetime.now().isoformat()
            )
        
        # Fallback to basic TTS
        else:
            from gtts import gTTS
            import pygame
            import tempfile
            
            text = request.text
            tts = gTTS(text=text, lang=request.language, slow=(request.voice_speed < 1.0))
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
                tts.save(tmp.name)
                pygame.mixer.init()
                pygame.mixer.music.load(tmp.name)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)
                
                pygame.mixer.quit()
                os.unlink(tmp.name)
            
            return TTSResponse(
                success=True,
                message=f"🔊 Played: '{text[:50]}...'",
                timestamp=datetime.now().isoformat()
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"🔊 TTS error: {e}")
        return TTSResponse(
            success=False,
            message=f"🔊 TTS error: {str(e)}",
            timestamp=datetime.now().isoformat()
        )

@app.post("/process-voice")
async def process_voice(audio_file: UploadFile = File(...)):
    """Enhanced voice processing with real speech recognition"""
    try:
        logger.info(f"🎤 Voice file received: {audio_file.filename}")
        
        # Use enhanced speech processor if available
        if SPEECH_PROCESSOR_AVAILABLE and enhanced_speech_processor:
            # For future implementation - real voice file processing
            return JSONResponse(
                content={
                    "success": False,
                    "message": "🎤 Voice file processing not yet implemented. Please use the microphone button in the frontend for real-time voice recognition!",
                    "intent": "voice_file_not_implemented",
                    "agent_used": "enhanced_speech_processor",
                    "timestamp": datetime.now().isoformat(),
                    "suggestion": "Use the microphone button in the frontend for real voice recognition"
                }
            )
        else:
            return JSONResponse(
                content={
                    "success": False,
                    "message": "🎤 Voice processing not available. Enhanced speech processor not loaded.",
                    "intent": "voice_not_available",
                    "agent_used": "none",
                    "timestamp": datetime.now().isoformat()
                }
            )
        
    except Exception as e:
        logger.error(f"🎤 Voice processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Voice processing error: {str(e)}")

@app.get("/agents")
async def get_agents():
    """Get enhanced list of available agents"""
    try:
        agents = []
        if AGENT_MANAGER_AVAILABLE and agent_manager:
            agents = agent_manager.get_available_agents()
        
        # Enhanced agent information
        agent_info = {
            "whatsapp": {
                "name": "Enhanced WhatsApp Agent",
                "description": "Send messages via WhatsApp with natural language and file sharing",
                "capabilities": ["Send messages", "Contact search", "URL generation", "File sharing"],
                "examples": ["Send WhatsApp to Mom: I'm coming home", "Share report.pdf with dad on whatsapp"]
            },
            "conversation": {
                "name": "Vaani (Conversational AI)",
                "description": "Natural conversation and assistance with enhanced NLP",
                "capabilities": ["Greetings", "Help guidance", "Natural chat", "Task clarification"],
                "examples": ["Hello", "What can you do?", "Help me", "Thank you"]
            },
            "filesearch": {
                "name": "Enhanced FileSearch Agent",
                "description": "Find, open, and share files across devices with real file system access",
                "capabilities": ["Real file search", "Cross-platform file opening", "File sharing prep", "Multiple search locations"],
                "examples": ["Find my report", "Open presentation.pptx", "Search for photos in downloads"]
            }
        }
        
        return {
            "success": True,
            "agents": agents,
            "agent_details": agent_info,
            "count": len(agents) if agents else 3,
            "multi_agent_support": True,
            "natural_language": True,
            "real_functionality": True,
            "crewai_orchestration": CREWAI_AVAILABLE,
            "enhanced_features": {
                "real_file_access": True,
                "enhanced_contacts": True,
                "voice_recognition": SPEECH_PROCESSOR_AVAILABLE,
                "cross_platform": True
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting agents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/execute-workflow")
async def execute_workflow(request: dict):
    """Execute workflow endpoint for frontend compatibility"""
    try:
        workflow_type = request.get("workflow_type", "general")
        parameters = request.get("parameters", {})
        command = parameters.get("command", "")
        
        logger.info(f"🎯 Executing {workflow_type} workflow with command: {command}")
        
        # Convert to CommandRequest and use existing process_command logic
        cmd_request = CommandRequest(command=command)
        result = await process_command(cmd_request)
        
        # Convert to frontend-expected format
        return {
            "success": result.success,
            "message": result.message,
            "intent": result.intent,
            "agent_used": result.agent_used,
            "timestamp": result.timestamp,
            "requires_popup": result.requires_popup,
            "whatsapp_url": result.whatsapp_url,
            "file_info": result.file_info,
            "workflow_type": workflow_type,
            "agents_used": [result.agent_used],
            "execution_time": 0,
            "workflow_id": f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "results": result.details or {}
        }
        
    except Exception as e:
        logger.error(f"❌ Execute workflow error: {e}")
        return {
            "success": False,
            "message": f"❌ Workflow error: {str(e)}",
            "intent": "error",
            "agent_used": "system",
            "timestamp": datetime.now().isoformat(),
            "workflow_type": workflow_type,
            "agents_used": [],
            "execution_time": 0,
            "workflow_id": "error",
            "results": {"error": str(e)}
        }

@app.get("/config")
async def get_config():
    """Get enhanced application configuration"""
    try:
        config_info = {
            "success": True,
            "version": "4.0.0 - Production Conversational AI with Voice & Memory",
            "features": {
                "crewai_available": CREWAI_AVAILABLE,
                "speech_processor_available": SPEECH_PROCESSOR_AVAILABLE,
                "agent_manager_available": AGENT_MANAGER_AVAILABLE,
                "config_available": CONFIG_AVAILABLE,
                "conversational_ai_available": CONVERSATIONAL_AI_AVAILABLE,
                "real_file_access": True,
                "enhanced_whatsapp": True,
                "websocket_support": True,
                "natural_voice_synthesis": True,
                "conversation_memory": True
            },
            "agents_available": agent_manager.get_available_agents() if AGENT_MANAGER_AVAILABLE and agent_manager else [],
            "search_locations": file_manager.search_locations,
            "available_contacts": list(whatsapp_manager.get_contact_list().keys()),
            "timestamp": datetime.now().isoformat()
        }
        
        # Add config details if available
        if CONFIG_AVAILABLE and config:
            config_info["config"] = {
                "groq_model": getattr(config, 'GROQ_MODEL', 'Not configured'),
                "fastapi_host": getattr(config, 'FASTAPI_HOST', '0.0.0.0'),
                "fastapi_port": getattr(config, 'FASTAPI_PORT', 8000),
                "agent_temperature": getattr(config, 'AGENT_TEMPERATURE', 0.1),
                "max_response_tokens": getattr(config, 'MAX_RESPONSE_TOKENS', 1000),
                "tts_engine": getattr(config, 'TTS_ENGINE', 'edge'),
                "voice_feedback_enabled": getattr(config, 'ENABLE_VOICE_FEEDBACK', True)
            }
        
        return config_info
    except Exception as e:
        logger.error(f"Error getting config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversation/history")
async def get_conversation_history(user_id: str = "default_user", limit: int = 50):
    """Get conversation history for user"""
    try:
        if CONVERSATIONAL_AI_AVAILABLE and conversation_memory:
            history = await conversation_memory.get_conversation_history(user_id, limit)
            return {
                "success": True,
                "history": history,
                "count": len(history),
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "message": "Conversation memory not available",
                "history": [],
                "count": 0
            }
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversation/analytics")
async def get_conversation_analytics(user_id: str = "default_user"):
    """Get conversation analytics for user"""
    try:
        if CONVERSATIONAL_AI_AVAILABLE and conversation_memory:
            analytics = await conversation_memory.get_conversation_analytics(user_id)
            return {
                "success": True,
                "analytics": analytics,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "message": "Conversation analytics not available",
                "analytics": {}
            }
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket Manager
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
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await ws_manager.send_message(websocket, {"type": "pong", "timestamp": datetime.now().isoformat()})
            
            elif message.get("type") == "command":
                command = message.get("command", "")
                if command:
                    # Process command (reuse existing logic)
                    request = CommandRequest(command=command)
                    result = await process_command(request)
                    
                    # Send result via WebSocket
                    await ws_manager.send_message(websocket, {
                        "type": "command_result",
                        "data": {
                            "success": result.success,
                            "message": result.message,
                            "intent": result.intent,
                            "agent_used": result.agent_used,
                            "timestamp": result.timestamp,
                            "requires_popup": result.requires_popup,
                            "whatsapp_url": result.whatsapp_url,
                            "file_info": result.file_info,
                            "agents_involved": [result.agent_used] if result.agent_used else [],
                            "execution_time": 0,
                            "workflow_id": f"ws_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            "results": result.details or {}
                        }
                    })
    
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        ws_manager.disconnect(websocket)

# Enhanced Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "message": "Endpoint not found",
            "timestamp": datetime.now().isoformat(),
            "available_endpoints": ["/", "/health", "/process-command", "/text-to-speech", "/agents", "/config", "/ws"]
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "timestamp": datetime.now().isoformat(),
            "suggestion": "Please check logs for details or contact support"
        }
    )

if __name__ == "__main__":
    # Enhanced startup with configuration validation
    logger.info("🚀 Starting Enhanced CrewAI Multi-Agent Backend...")
    
    # Validate configuration before starting
    if CONFIG_AVAILABLE and config:
        if not config.validate_config():
            logger.error("❌ Configuration validation failed. Please check your .env file.")
            logger.info("📄 Required environment variables: GROQ_API_KEY")
        else:
            logger.info("✅ Configuration validated successfully!")
    else:
        logger.warning("⚠️  Configuration not available. Some features may not work.")
    
    # Component availability summary
    logger.info(f"📊 Component Status:")
    logger.info(f"   🤖 CrewAI Orchestration: {'✅' if CREWAI_AVAILABLE else '❌'}")
    logger.info(f"   🎤 Enhanced Speech Processor: {'✅' if SPEECH_PROCESSOR_AVAILABLE else '❌'}")
    logger.info(f"   🎯 Real Agent Manager: {'✅' if AGENT_MANAGER_AVAILABLE else '❌'}")
    logger.info(f"   📁 Enhanced File Manager: ✅")
    logger.info(f"   📱 Enhanced WhatsApp Manager: ✅")
    logger.info(f"   🔌 WebSocket Support: ✅")
    
    # Use port 8000 for Next.js frontend integration
    HOST = "0.0.0.0"
    PORT = 8000
    
    logger.info(f"🚀 Starting Enhanced FastAPI server on {HOST}:{PORT}")
    logger.info(f"📡 API available at: http://localhost:{PORT}")
    logger.info(f"🌐 Next.js frontend should connect to: http://localhost:{PORT}")
    logger.info(f"🔌 WebSocket endpoint: ws://localhost:{PORT}/ws")
    
    uvicorn.run(
        "crew_main:app",
        host=HOST,
        port=PORT,
        reload=True,
        log_level="info"
    )