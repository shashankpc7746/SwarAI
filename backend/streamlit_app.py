"""
Streamlit Frontend for AI Task Automation Assistant
Voice-powered interface for task automation
"""

import streamlit as st

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="AI Task Automation Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Now import other modules
import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional
import time

from config import config
from utils.enhanced_speech_processor import enhanced_speech_processor

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .voice-button {
        background-color: #ff6b6b;
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 0.5rem;
        font-size: 1.2rem;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

class StreamlitApp:
    """Main Streamlit application class"""
    
    def __init__(self):
        self.api_base_url = f"http://{config.FASTAPI_HOST}:{config.FASTAPI_PORT}"
        self.init_session_state()
        # Display enhanced speech processor status
        try:
            enhanced_speech_processor.display_status()
        except Exception as e:
            st.info("ℹ️ Enhanced audio system will initialize when needed")
    
    def init_session_state(self):
        """Initialize Streamlit session state"""
        if "command_history" not in st.session_state:
            st.session_state.command_history = []
        if "is_listening" not in st.session_state:
            st.session_state.is_listening = False
        if "backend_status" not in st.session_state:
            st.session_state.backend_status = "unknown"
    
    def check_backend_status(self) -> bool:
        """Check if FastAPI backend is running"""
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            if response.status_code == 200:
                st.session_state.backend_status = "online"
                return True
            else:
                st.session_state.backend_status = "error"
                return False
        except requests.exceptions.RequestException:
            st.session_state.backend_status = "offline"
            return False
    
    def send_command_to_backend(self, command: str) -> Dict[str, Any]:
        """Send command to FastAPI backend"""
        try:
            payload = {"command": command}
            response = requests.post(
                f"{self.api_base_url}/process-command",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "message": f"❌ Backend error: {response.status_code}",
                    "intent": "error",
                    "agent_used": "none",
                    "timestamp": datetime.now().isoformat()
                }
        
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": f"❌ Connection error: {str(e)}",
                "intent": "error", 
                "agent_used": "none",
                "timestamp": datetime.now().isoformat()
            }
    
    def process_voice_input(self) -> Optional[str]:
        """Process voice input using enhanced speech recognition only"""
        try:
            # Use enhanced processor with multi-engine support
            with st.spinner("🎤 Listening with enhanced multi-engine recognition..."):
                success, result = enhanced_speech_processor.listen_for_speech_enhanced(
                    timeout=config.SPEECH_TIMEOUT,
                    phrase_time_limit=config.SPEECH_PHRASE_TIME_LIMIT
                )
            
            if success:
                st.success(f"🎤 Enhanced recognition heard: '{result}'")
                return result
            else:
                st.error(result)
                return None
                
        except Exception as e:
            st.error(f"❌ Voice processing error: {str(e)}")
            return None
    
    def add_to_history(self, command: str, response: Dict[str, Any]):
        """Add command and response to history"""
        history_item = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "command": command,
            "response": response
        }
        st.session_state.command_history.insert(0, history_item)
        
        # Keep only last 10 items
        if len(st.session_state.command_history) > 10:
            st.session_state.command_history = st.session_state.command_history[:10]
    
    def render_header(self):
        """Render application header"""
        st.markdown('<h1 class="main-header">🤖 AI Task Automation Assistant</h1>', unsafe_allow_html=True)
        st.markdown("### Voice-Powered Daily Task Automation")
        
        # Backend status
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("🔄 Check Backend"):
                self.check_backend_status()
        
        with col2:
            status_color = {
                "online": "🟢",
                "offline": "🔴", 
                "error": "🟡",
                "unknown": "⚪"
            }
            st.write(f"Backend: {status_color.get(st.session_state.backend_status, '⚪')} {st.session_state.backend_status}")
        
        with col3:
            if st.session_state.backend_status != "online":
                st.warning("⚠️ Backend not available. Please start the FastAPI server first.")
    
    def render_main_interface(self):
        """Render main user interface"""
        # Command input section
        st.markdown("### 🎯 Give Your Command")
        
        # Voice and text input tabs
        tab1, tab2 = st.tabs(["🎤 Voice Input", "⌨️ Text Input"])
        
        with tab1:
            self.render_voice_interface()
        
        with tab2:
            self.render_text_interface()
    
    def render_voice_interface(self):
        """Render voice input interface"""
        st.markdown("#### Voice Commands")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("🎤 Start Voice Command", type="primary", use_container_width=True):
                if st.session_state.backend_status == "online":
                    command = self.process_voice_input()
                    if command:
                        self.process_command(command, is_voice=True)
                else:
                    st.error("❌ Backend not available!")
        
        with col2:
            if st.button("🔧 Test Microphone", use_container_width=True):
                with st.spinner("Testing microphone with enhanced recognition..."):
                    success, message = enhanced_speech_processor.test_microphone_enhanced()
                
                if success:
                    st.success(message)
                else:
                    st.error(message)
        
        # Enhanced voice tips
        with st.expander("💡 Enhanced Voice Command Tips"):
            st.markdown("""
            **Supported Commands:**
            - "Send WhatsApp to Jay: Hello how are you"
            - "Message Mom on WhatsApp: I'll be late"
            - "WhatsApp Vijay: Meeting at 5 PM"
            
            **Enhanced Features:**
            - 🎆 **Multiple Recognition Engines**: Google + Whisper AI fallback
            - 🔊 **Improved TTS**: Multiple audio systems with fallback
            - 🎤 **Better Accuracy**: Enhanced noise reduction and language support
            - 🌍 **Multi-Language**: en-US, en-IN, en-GB support
            
            **Tips for Best Results:**
            - Speak clearly and at normal pace
            - Include recipient name and message
            - Wait for the listening indicator
            - Minimize background noise
            - Ensure stable internet connection
            - Start speaking immediately after clicking voice button
            """)
    
    def render_text_interface(self):
        """Render text input interface"""
        st.markdown("#### Text Commands")
        
        # Text input
        command = st.text_input(
            "Enter your command:",
            placeholder="e.g., Send WhatsApp to Jay: Hello how are you",
            key="text_command"
        )
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if st.button("📤 Send Command", type="primary", use_container_width=True):
                if command.strip():
                    if st.session_state.backend_status == "online":
                        self.process_command(command.strip(), is_voice=False)
                        st.session_state.text_command = ""  # Clear input
                    else:
                        st.error("❌ Backend not available!")
                else:
                    st.warning("⚠️ Please enter a command")
        
        # Text examples
        st.markdown("**Example Commands:**")
        examples = [
            "Send WhatsApp to Jay: Hello how are you",
            "Message Mom on WhatsApp: I'll be late today",
            "WhatsApp Vijay: Can we reschedule the meeting?"
        ]
        
        for example in examples:
            if st.button(f"📝 {example}", key=f"example_{example[:20]}"):
                if st.session_state.backend_status == "online":
                    self.process_command(example, is_voice=False)
                else:
                    st.error("❌ Backend not available!")
    
    def process_command(self, command: str, is_voice: bool = False):
        """Process a command through the backend"""
        with st.spinner("🔄 Processing your command..."):
            response = self.send_command_to_backend(command)
        
        # Add to history
        self.add_to_history(command, response)
        
        # Display result
        if response.get("success", False):
            st.success(f"✅ {response.get('message', 'Command processed successfully!')}")
            
            # Enhanced text-to-speech for successful commands
            if is_voice:
                with st.spinner("🔊 Speaking response with enhanced TTS..."):
                    enhanced_speech_processor.text_to_speech_enhanced(response.get('message', ''))
            
            # Show WhatsApp URL if available
            if response.get("details", {}).get("agent_response", {}).get("whatsapp_url"):
                whatsapp_url = response["details"]["agent_response"]["whatsapp_url"]
                st.markdown(f"**🔗 WhatsApp Link:** [Click to send message]({whatsapp_url})")
        else:
            st.error(f"❌ {response.get('message', 'Command failed')}")
            
            # Enhanced text-to-speech for errors
            if is_voice:
                error_msg = "Command failed. Please try again."
                enhanced_speech_processor.text_to_speech_enhanced(error_msg)
    
    def render_sidebar(self):
        """Render sidebar with additional information"""
        with st.sidebar:
            st.markdown("### 📊 System Status")
            
            # Backend status
            status_emoji = {
                "online": "🟢",
                "offline": "🔴",
                "error": "🟡", 
                "unknown": "⚪"
            }
            st.write(f"**Backend:** {status_emoji.get(st.session_state.backend_status, '⚪')} {st.session_state.backend_status}")
            
            # Available agents
            if st.session_state.backend_status == "online":
                try:
                    response = requests.get(f"{self.api_base_url}/agents", timeout=5)
                    if response.status_code == 200:
                        agents_data = response.json()
                        st.write(f"**Agents:** {agents_data.get('count', 0)} available")
                        for agent in agents_data.get('agents', []):
                            st.write(f"  • {agent}")
                except:
                    st.write("**Agents:** Unable to fetch")
            
            st.markdown("---")
            
            # Quick actions
            st.markdown("### ⚡ Quick Actions")
            
            if st.button("🔄 Refresh Status", use_container_width=True):
                self.check_backend_status()
                st.rerun()
            
            if st.button("🗑️ Clear History", use_container_width=True):
                st.session_state.command_history = []
                st.success("History cleared!")
            
            # Settings
            st.markdown("### ⚙️ Settings")
            
            # Speech settings
            with st.expander("🎤 Speech Settings"):
                st.write(f"Timeout: {config.SPEECH_TIMEOUT}s")
                st.write(f"Phrase limit: {config.SPEECH_PHRASE_TIME_LIMIT}s")
                
                # Enhanced audio devices
                st.write("**Enhanced Audio System:**")
                try:
                    devices = enhanced_speech_processor.get_audio_devices_enhanced()
                    for device in devices[:10]:  # Show more devices
                        st.write(f"  • {device}")
                except Exception as e:
                    st.warning(f"Audio device info failed: {str(e)}")
    
    def render_history(self):
        """Render command history"""
        st.markdown("### 📜 Command History")
        
        if not st.session_state.command_history:
            st.info("No commands yet. Try saying 'Send WhatsApp to Jay: Hello!'")
            return
        
        for item in st.session_state.command_history:
            with st.expander(f"🕒 {item['timestamp']} - {item['command'][:50]}..."):
                st.write(f"**Command:** {item['command']}")
                st.write(f"**Success:** {'✅' if item['response'].get('success') else '❌'}")
                st.write(f"**Agent:** {item['response'].get('agent_used', 'unknown')}")
                st.write(f"**Response:** {item['response'].get('message', 'No message')}")
                
                if item['response'].get('details', {}).get('agent_response', {}).get('whatsapp_url'):
                    url = item['response']['details']['agent_response']['whatsapp_url']
                    st.markdown(f"**WhatsApp URL:** [Click here]({url})")
    
    def run(self):
        """Run the Streamlit application"""
        try:
            # Check backend on startup
            if st.session_state.backend_status == "unknown":
                self.check_backend_status()
            
            # Render UI components
            self.render_header()
            self.render_sidebar()
            self.render_main_interface()
            
            st.markdown("---")
            self.render_history()
            
            # Footer
            st.markdown("---")
            st.markdown("### 🎯 Enhanced Features")
            st.markdown("""
            - **🚀 WhatsApp Agent**: Send messages via voice/text commands
            - **🎤 Multi-Engine Voice Recognition**: Google + Whisper AI + fallback engines
            - **🔊 Enhanced Text-to-Speech**: Multiple TTS systems with audio playback
            - **📇 Smart Contact Search**: Find contacts by name with fuzzy matching
            - **🔗 URL Generation**: Create WhatsApp deep links instantly
            - **🌍 Multi-Language Support**: en-US, en-IN, en-GB recognition
            - **🔧 Audio System Diagnostics**: Real-time audio system monitoring
            """)
            
            st.markdown("### 🚀 Coming Soon")
            st.markdown("""
            - **File Search Agent**: Find and open files
            - **Calendar Agent**: Schedule meetings and events
            - **Call Agent**: Make phone calls
            - **Notes Agent**: Voice note-taking
            - **Email Agent**: Send and manage emails
            """)
        
        except Exception as e:
            st.error(f"Application error: {str(e)}")
            st.info("Please refresh the page or restart the application.")

# Create and run the app with error handling
if __name__ == "__main__":
    try:
        app = StreamlitApp()
        app.run()
    except Exception as e:
        st.error(f"Failed to initialize app: {str(e)}")
        st.info("Please check your configuration and try again.")
else:
    # When imported as module, create app instance
    try:
        app = StreamlitApp()
        app.run()
    except Exception as e:
        st.error(f"App initialization error: {str(e)}")