"""
Configuration module for AI Task Automation Assistant
Handles environment variables and application settings
"""

import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

class Config:
    """Application configuration class"""
    
    # AI/LLM Configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama3-70b-8192")
    
    # WhatsApp Configuration
    WHATSAPP_API_KEY: str = os.getenv("WHATSAPP_API_KEY", "demo_whatsapp_api_key_12345")
    WHATSAPP_PHONE_NUMBER_ID: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "demo_phone_id_67890")
    
    # Server Configuration
    FASTAPI_HOST: str = os.getenv("FASTAPI_HOST", "127.0.0.1")
    FASTAPI_PORT: int = int(os.getenv("FASTAPI_PORT", "8000"))
    STREAMLIT_PORT: int = int(os.getenv("STREAMLIT_PORT", "8501"))
    
    # Speech Configuration
    SPEECH_TIMEOUT: int = int(os.getenv("SPEECH_TIMEOUT", "5"))
    SPEECH_PHRASE_TIME_LIMIT: int = int(os.getenv("SPEECH_PHRASE_TIME_LIMIT", "10"))
    
    # Agent Configuration
    AGENT_TEMPERATURE: float = float(os.getenv("AGENT_TEMPERATURE", "0.1"))
    MAX_RESPONSE_TOKENS: int = int(os.getenv("MAX_RESPONSE_TOKENS", "1000"))
    
    # MongoDB Configuration
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DATABASE: str = os.getenv("MONGODB_DATABASE", "vaani_assistant")
    
    # Enhanced TTS Configuration (Free Services)
    TTS_ENGINE: str = os.getenv("TTS_ENGINE", "edge")  # edge, coqui, pyttsx3, gtts, festival
    VAANI_VOICE: str = os.getenv("VAANI_VOICE", "en-US-AriaNeural")  # Edge TTS voice
    VAANI_VOICE_SPEED: float = float(os.getenv("VAANI_VOICE_SPEED", "1.0"))
    VAANI_VOICE_PITCH: str = os.getenv("VAANI_VOICE_PITCH", "+0Hz")
    COQUI_MODEL: str = os.getenv("COQUI_MODEL", "tts_models/en/ljspeech/tacotron2-DDC")
    PYTTSX3_RATE: int = int(os.getenv("PYTTSX3_RATE", "180"))
    PYTTSX3_VOLUME: float = float(os.getenv("PYTTSX3_VOLUME", "0.9"))
    
    # Conversational AI Settings
    CONVERSATION_MEMORY_LIMIT: int = int(os.getenv("CONVERSATION_MEMORY_LIMIT", "50"))
    ENABLE_VOICE_FEEDBACK: bool = os.getenv("ENABLE_VOICE_FEEDBACK", "true").lower() == "true"
    
    # Email Configuration
    EMAIL_CLIENT: str = os.getenv("EMAIL_CLIENT", "default")
    DEFAULT_EMAIL_FROM: str = os.getenv("DEFAULT_EMAIL_FROM", "your-email@gmail.com")
    
    # Calendar Configuration
    CALENDAR_APP: str = os.getenv("CALENDAR_APP", "default")
    
    # Phone Configuration
    PHONE_APP: str = os.getenv("PHONE_APP", "default")
    
    # Payment Configuration
    PAYMENT_APPS: str = os.getenv("PAYMENT_APPS", "paypal,googlepay,paytm,phonepe")
    
    # Application Launcher Configuration
    BROWSER_DEFAULT: str = os.getenv("BROWSER_DEFAULT", "chrome")
    EDITOR_DEFAULT: str = os.getenv("EDITOR_DEFAULT", "notepad")
    
    # File Search Configuration
    SEARCH_DIRECTORIES: str = os.getenv("SEARCH_DIRECTORIES", "C:\\Users,C:\\Documents,C:\\Downloads")
    MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", "10"))
    
    # Task Configuration
    TASK_STORAGE: str = os.getenv("TASK_STORAGE", "local")
    REMINDER_NOTIFICATIONS: bool = os.getenv("REMINDER_NOTIFICATIONS", "true").lower() == "true"
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate essential configuration"""
        if not cls.GROQ_API_KEY or cls.GROQ_API_KEY == "your_groq_api_key_here":
            print("⚠️  Warning: GROQ_API_KEY not set properly. Please update .env file.")
            return False
        return True

# Create global config instance
config = Config()