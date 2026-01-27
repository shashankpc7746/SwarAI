"""
Enhanced Speech Processing Utilities for AI Task Automation Assistant
Ultra-optimized version to prevent app crashes with proper lazy loading
"""

import speech_recognition as sr
import os
import tempfile
import time
from typing import Optional, Tuple, List
import streamlit as st
from config import config
from .conversational_tts import conversational_tts

# Enhanced imports with ultra-safe fallbacks and optimizations
try:
    # Suppress pygame welcome message before import
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
    import pygame
    pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import whisper
    WHISPER_AVAILABLE = True
    # Suppress Whisper warnings
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning, module="whisper")
except ImportError:
    WHISPER_AVAILABLE = False

try:
    # Suppress warnings for better stability
    import warnings
    warnings.filterwarnings("ignore", category=RuntimeWarning, module="pydub")
    from pydub import AudioSegment
    from pydub.playback import play
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

class EnhancedSpeechProcessor:
    """Ultra-stable enhanced speech processor with proper lazy initialization"""
    
    def __init__(self):
        # Ultra-minimal initialization to prevent app crashes
        self.initialized = False
        self.audio_initialized = False
        self.whisper_loaded = False
        self._whisper_model = None
        
        # Set default flags - avoid heavy initialization during import
        self.recognition_engines = {
            'google': True,  # Always available with speech_recognition
            'whisper': WHISPER_AVAILABLE,  # Check availability but don't load
            'vosk': False  # Disabled for stability
        }
        
        self.audio_systems = {
            'pygame': PYGAME_AVAILABLE,
            'gtts': GTTS_AVAILABLE,
            'pydub': PYDUB_AVAILABLE
        }
        
        # Only initialize basic speech recognition - defer everything else
        try:
            self.recognizer = sr.Recognizer()
            # Apply memory specifications for speech recognition
            self.recognizer.energy_threshold = 300
            self.recognizer.pause_threshold = 0.8
            self.recognizer.dynamic_energy_adjustment = True
            
            self.microphone = sr.Microphone()
            self.initialized = True
        except Exception:
            # Silent fail during import to prevent app crashes
            self.initialized = False
    
    def display_status(self):
        """Display enhanced system status with safe initialization"""
        with st.expander("🚀 Enhanced Audio System Status"):
            st.write("**Core System:**")
            if self.initialized:
                st.success("✅ Enhanced speech recognition: Ready")
            else:
                st.warning("⚠️ Enhanced speech recognition: Will initialize on first use")
            
            st.write("**Speech Recognition Engines:**")
            st.write(f"  • Google Speech: {'✅ Available' if self.recognition_engines.get('google') else '❌ Not available'}")
            st.write(f"  • Whisper AI: {'✅ Available (loads on demand)' if self.recognition_engines.get('whisper') else '❌ Not installed'}")
            
            st.write("**Audio Systems:**")
            st.write(f"  • Pygame: {'✅ Available' if self.audio_systems.get('pygame') else '❌ Not available'}")
            st.write(f"  • Google TTS: {'✅ Available' if self.audio_systems.get('gtts') else '❌ Not available'}")
            st.write(f"  • Pydub: {'✅ Available' if self.audio_systems.get('pydub') else '❌ Not available'}")
            
            if self.whisper_loaded:
                st.success("🤖 Whisper AI model: Loaded and ready")
            elif self.recognition_engines.get('whisper'):
                st.info("🤖 Whisper AI model: Will load automatically when needed")
            else:
                st.info("🤖 Whisper AI: Not available (install with: pip install openai-whisper)")
            
            st.info("💡 All components use lazy loading for optimal performance")
    
    def _ensure_initialized(self) -> bool:
        """Ultra-safe initialization with error handling"""
        if self.initialized:
            return True
            
        try:
            # Basic speech recognition setup
            if not hasattr(self, 'recognizer'):
                self.recognizer = sr.Recognizer()
                # Apply memory specifications
                self.recognizer.energy_threshold = 300
                self.recognizer.pause_threshold = 0.8
                self.recognizer.dynamic_energy_adjustment = True
                
            if not hasattr(self, 'microphone'):
                self.microphone = sr.Microphone()
                
            self.initialized = True
            return True
            
        except Exception as e:
            # Only show error in Streamlit context, not during import
            if 'streamlit' in str(type(st)):
                st.error(f"❌ Speech initialization failed: {str(e)}")
            return False
    
    def _ensure_whisper_ready(self) -> bool:
        """Load Whisper model if available and needed"""
        if self.whisper_loaded or not self.recognition_engines.get('whisper'):
            return self.whisper_loaded
            
        try:
            if WHISPER_AVAILABLE:
                with st.spinner("🤖 Loading Whisper AI model (first use only)..."):
                    self._whisper_model = whisper.load_model("base")
                self.whisper_loaded = True
                st.success("🤖 Whisper AI loaded successfully!")
                return True
        except Exception as e:
            st.warning(f"Whisper loading failed: {str(e)}")
            self.recognition_engines['whisper'] = False
            
        return False
    
    def _ensure_audio_ready(self) -> bool:
        """Ultra-safe audio initialization to prevent crashes"""
        if self.audio_initialized:
            return True
            
        try:
            if self.audio_systems.get('pygame') and PYGAME_AVAILABLE:
                # Safe pygame initialization
                if not pygame.get_init():
                    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                self.audio_initialized = True
                return True
        except Exception:
            # Silent fail to prevent app crashes
            self.audio_systems['pygame'] = False
            
        return False
    
    def listen_for_speech_enhanced(self, timeout: int = 10, phrase_time_limit: int = 20) -> Tuple[bool, str]:
        """Enhanced speech recognition with multi-engine support and increased listening time"""
        
        # Ensure basic components are ready
        if not self._ensure_initialized():
            return False, "❌ Speech recognition not available"
            
        try:
            # Calibrate microphone (1.5s as per memory specs)
            with self.microphone as source:
                st.info("🎤 Calibrating microphone...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1.5)
                
                # Listen for speech with extended timeouts
                st.info("🎤 Listening with enhanced recognition... (Speak now!)")
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,  # Extended to 10 seconds
                    phrase_time_limit=phrase_time_limit  # Extended to 20 seconds
                )
            
            # Try multiple recognition engines
            return self._recognize_with_engines(audio)
            
        except sr.WaitTimeoutError:
            return False, "⏰ Listening timeout. No speech detected."
        except Exception as e:
            return False, f"❌ Speech error: {str(e)}"
    
    def _recognize_with_engines(self, audio) -> Tuple[bool, str]:
        """Try multiple speech recognition engines with fallback"""
        
        # Engine 1: Google Speech Recognition (Primary)
        if self.recognition_engines.get('google'):
            try:
                st.info("🔄 Processing with Google Speech Recognition...")
                # Try multiple languages as per memory specifications
                for language in ["en-US", "en-IN", "en-GB", "en-AU"]:
                    try:
                        text = self.recognizer.recognize_google(audio, language=language)
                        if text.strip():
                            return True, text.strip()
                    except sr.UnknownValueError:
                        continue
            except sr.RequestError:
                pass
        
        # Engine 2: Whisper AI (Secondary)
        if self._ensure_whisper_ready():
            try:
                st.info("🔄 Processing with Whisper AI...")
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                    wav_data = audio.get_wav_data()
                    tmp_file.write(wav_data)
                    tmp_file.flush()
                    
                    result = self._whisper_model.transcribe(tmp_file.name)
                    text = result['text'].strip()
                    
                    os.unlink(tmp_file.name)
                    
                    if text:
                        return True, text
            except Exception as e:
                st.warning(f"Whisper recognition failed: {str(e)}")
        
        return False, "🔇 Could not understand speech. Please try again."
    
    def text_to_speech_enhanced(self, text: str, language: str = 'en') -> bool:
        """Production-level conversational text-to-speech"""
        
        if not text or not text.strip():
            return False
        
        try:
            # Use conversational TTS for natural speech
            success = conversational_tts.speak_threaded(text)
            
            if success:
                return True
            else:
                # Fallback to basic TTS
                return self._fallback_tts(text, language)
                
        except Exception as e:
            print(f"🔊 Enhanced TTS error: {e}")
            return self._fallback_tts(text, language)
    
    def _fallback_tts(self, text: str, language: str = 'en') -> bool:
        """Fallback TTS implementation"""
        try:
            if self.audio_systems.get('gtts'):
                # Ensure audio is ready
                audio_ready = self._ensure_audio_ready()
                
                if not audio_ready:
                    print(f"🔊 SwarAI says: '{text}' (Audio playback not available)")
                    return True
                
                # Create and play TTS
                tts = gTTS(text=text, lang=language, slow=False)
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                    tts.save(tmp_file.name)
                    
                    pygame.mixer.music.load(tmp_file.name)
                    pygame.mixer.music.play()
                    
                    # Wait for completion
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)
                    
                    pygame.mixer.music.unload()
                    os.unlink(tmp_file.name)
                    
                    return True
            else:
                print(f"🔊 SwarAI says: '{text}'")
                return True
                
        except Exception as e:
            print(f"🔊 SwarAI says: '{text}' (TTS error: {str(e)})")
            return True
    
    def test_microphone_enhanced(self) -> Tuple[bool, str]:
        """Test microphone with enhanced recognition"""
        
        if not self._ensure_initialized():
            return False, "❌ Speech system not available"
            
        try:
            st.info("🔧 Testing microphone with enhanced recognition...")
            
            with self.microphone as source:
                # Quick calibration
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                
                # Test recording
                st.info("🎤 Say something for 3 seconds...")
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=5)
                
                # Test recognition
                success, result = self._recognize_with_engines(audio)
                
                if success:
                    return True, f"✅ Enhanced microphone test successful! Heard: '{result}'"
                else:
                    return False, f"❌ Test failed: {result}"
                    
        except sr.WaitTimeoutError:
            return False, "⏰ Test timeout. Try speaking during the test."
        except Exception as e:
            return False, f"❌ Test failed: {str(e)}"
    
    def get_audio_devices_enhanced(self) -> List[str]:
        """Get enhanced audio device information"""
        devices = []
        
        try:
            if self.initialized:
                devices.append("🎤 **Microphone Devices:**")
                mic_list = sr.Microphone.list_microphone_names()
                for i, device in enumerate(mic_list[:5]):
                    devices.append(f"  {i}: {device}")
            else:
                devices.append("❌ **Microphone**: Not initialized")
        except Exception:
            devices.append("❌ **Microphone**: Error accessing devices")
        
        devices.append("🔊 **Audio Systems:**")
        for system, available in self.audio_systems.items():
            status = "✅" if available else "❌"
            devices.append(f"  {status} {system.upper()}")
        
        devices.append("🤖 **Recognition Engines:**")
        for engine, available in self.recognition_engines.items():
            status = "✅" if available else "❌"
            devices.append(f"  {status} {engine.upper()}")
        
        return devices

# Global enhanced speech processor instance
enhanced_speech_processor = EnhancedSpeechProcessor()