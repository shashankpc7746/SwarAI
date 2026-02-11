"""
Production-Level Conversational Text-to-Speech System
Using the best free TTS engines with natural voice synthesis
"""

import asyncio
import os
import tempfile
import logging
import threading
from typing import Optional, Dict, Any, List
from pathlib import Path
import json
import time

# Free TTS Libraries
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

try:
    from TTS.api import TTS
    COQUI_AVAILABLE = True
except ImportError:
    COQUI_AVAILABLE = False

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# Audio playback
try:
    import pygame
    try:
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
        PYGAME_AVAILABLE = True
    except Exception:
        PYGAME_AVAILABLE = False
except ImportError:
    PYGAME_AVAILABLE = False

try:
    import soundfile as sf
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False

from config import config

logger = logging.getLogger(__name__)

class ConversationalTTS:
    """
    Production-level conversational TTS with multiple free engines
    Designed for natural, human-like speech synthesis
    """
    
    def __init__(self):
        self.config = config
        self.current_engine = None
        self.voice_cache = {}
        self.is_speaking = False
        self._init_engines()
        
        # SwarAI personality voice settings
        self.SwarAI_personality = {
            "tone": "friendly",
            "pace": "moderate",
            "expressiveness": "high",
            "conversational_markers": ["Well,", "You know,", "Actually,", "Let me help you with that"]
        }
    
    def _init_engines(self):
        """Initialize available TTS engines"""
        self.engines = {}
        
        # 1. Edge TTS (Microsoft - Best Free Option)
        if EDGE_TTS_AVAILABLE:
            self.engines['edge'] = {
                'available': True,
                'quality': 'excellent',
                'voices': self._get_edge_voices(),
                'async': True
            }
            logger.info("✅ Edge TTS initialized - Premium quality free TTS")
        
        # 2. Coqui TTS (Open Source - High Quality)
        if COQUI_AVAILABLE:
            try:
                self.coqui_tts = TTS(model_name=self.config.COQUI_MODEL, progress_bar=False)
                self.engines['coqui'] = {
                    'available': True,
                    'quality': 'high',
                    'voices': ['default'],
                    'async': False
                }
                logger.info("✅ Coqui TTS initialized - Open source neural TTS")
            except Exception as e:
                logger.warning(f"Coqui TTS initialization failed: {e}")
        
        # 3. Pyttsx3 (Cross-platform - Fast)
        if PYTTSX3_AVAILABLE:
            try:
                engine = pyttsx3.init()
                voices = engine.getProperty('voices')
                self.engines['pyttsx3'] = {
                    'available': True,
                    'quality': 'good',
                    'voices': [v.id for v in voices] if voices else ['default'],
                    'async': False,
                    'engine': engine
                }
                logger.info("✅ Pyttsx3 initialized - System TTS engine")
            except Exception as e:
                logger.warning(f"Pyttsx3 initialization failed: {e}")
        
        # 4. Google TTS (Fallback)
        if GTTS_AVAILABLE:
            self.engines['gtts'] = {
                'available': True,
                'quality': 'good',
                'voices': ['en', 'en-us', 'en-uk', 'en-au'],
                'async': False
            }
            logger.info("✅ Google TTS initialized - Reliable fallback")
        
        # Select best available engine
        self._select_best_engine()
    
    def _get_edge_voices(self) -> List[str]:
        """Get available Edge TTS voices"""
        try:
            # Popular English voices for conversational AI
            return [
                "en-US-AriaNeural",     # Female, natural
                "en-US-JennyNeural",    # Female, friendly
                "en-US-GuyNeural",      # Male, natural
                "en-US-DavisNeural",    # Male, conversational
                "en-GB-SoniaNeural",    # British Female
                "en-AU-NatashaNeural",  # Australian Female
                "en-IN-NeerjaNeural"    # Indian English Female
            ]
        except Exception:
            return ["en-US-AriaNeural"]
    
    def _select_best_engine(self):
        """Select the best available TTS engine"""
        priority = ['edge', 'coqui', 'pyttsx3', 'gtts']
        
        for engine_name in priority:
            if engine_name in self.engines and self.engines[engine_name]['available']:
                self.current_engine = engine_name
                logger.info(f"🎤 Selected TTS Engine: {engine_name} ({self.engines[engine_name]['quality']} quality)")
                break
        
        if not self.current_engine:
            logger.error("❌ No TTS engines available")
    
    async def speak_async(self, text: str, voice: Optional[str] = None) -> bool:
        """
        Asynchronous speech synthesis with natural conversation flow
        """
        if not text or not text.strip():
            return False
        
        if self.is_speaking:
            logger.info("🎤 Speech in progress, queuing...")
            
        self.is_speaking = True
        
        try:
            # Add conversational naturalness
            enhanced_text = self._enhance_conversational_text(text)
            
            # Use best available engine
            if self.current_engine == 'edge':
                success = await self._speak_edge(enhanced_text, voice)
            elif self.current_engine == 'coqui':
                success = await self._speak_coqui(enhanced_text)
            elif self.current_engine == 'pyttsx3':
                success = await self._speak_pyttsx3(enhanced_text)
            else:
                success = await self._speak_gtts(enhanced_text)
            
            return success
            
        except Exception as e:
            logger.error(f"❌ TTS Error: {e}")
            return False
        finally:
            self.is_speaking = False
    
    def speak(self, text: str, voice: Optional[str] = None) -> bool:
        """Synchronous speech synthesis"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(self.speak_async(text, voice))
        except Exception as e:
            logger.error(f"❌ Sync TTS Error: {e}")
            return False
    
    def speak_threaded(self, text: str, voice: Optional[str] = None):
        """Non-blocking speech synthesis"""
        def _speak_thread():
            self.speak(text, voice)
        
        thread = threading.Thread(target=_speak_thread, daemon=True)
        thread.start()
    
    def _enhance_conversational_text(self, text: str) -> str:
        """Add natural conversation markers and pacing"""
        # Remove technical markers
        text = text.replace('✅', '').replace('❌', '').replace('📱', '').replace('📁', '').replace('🔄', '')
        text = text.replace('🎤', '').replace('💬', '').replace('📄', '').replace('🔍', '').replace('💡', '')
        
        # Add natural pauses for better flow
        text = text.replace('\n\n', '. ')
        text = text.replace('\n', '. ')
        text = text.replace(': ', ', ')
        
        # Add conversational naturalness
        if len(text) > 100:
            # Add breathing room for long responses
            sentences = text.split('. ')
            if len(sentences) > 2:
                text = '. '.join(sentences[:2]) + '. ' + '. '.join(sentences[2:])
        
        return text.strip()
    
    async def _speak_edge(self, text: str, voice: Optional[str] = None) -> bool:
        """Microsoft Edge TTS - Premium quality"""
        try:
            voice_name = voice or self.config.SwarAI_VOICE or "en-US-AriaNeural"
            
            # Create Edge TTS communicate object
            communicate = edge_tts.Communicate(text, voice_name)
            
            # Generate audio to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                await communicate.save(tmp_file.name)
                
                # Play audio
                return self._play_audio_file(tmp_file.name)
                
        except Exception as e:
            logger.error(f"Edge TTS error: {e}")
            return False
    
    async def _speak_coqui(self, text: str) -> bool:
        """Coqui TTS - Open source neural TTS"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                self.coqui_tts.tts_to_file(text=text, file_path=tmp_file.name)
                return self._play_audio_file(tmp_file.name)
        except Exception as e:
            logger.error(f"Coqui TTS error: {e}")
            return False
    
    async def _speak_pyttsx3(self, text: str) -> bool:
        """Pyttsx3 - System TTS"""
        try:
            engine = self.engines['pyttsx3']['engine']
            
            # Configure voice properties
            engine.setProperty('rate', self.config.PYTTSX3_RATE)
            engine.setProperty('volume', self.config.PYTTSX3_VOLUME)
            
            # Set voice if available
            voices = engine.getProperty('voices')
            if voices:
                for voice in voices:
                    if 'female' in voice.name.lower() or 'aria' in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
            
            engine.say(text)
            engine.runAndWait()
            return True
            
        except Exception as e:
            logger.error(f"Pyttsx3 error: {e}")
            return False
    
    async def _speak_gtts(self, text: str) -> bool:
        """Google TTS - Fallback option"""
        try:
            tts = gTTS(text=text, lang='en', slow=False)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tts.save(tmp_file.name)
                return self._play_audio_file(tmp_file.name)
                
        except Exception as e:
            logger.error(f"Google TTS error: {e}")
            return False
    
    def _play_audio_file(self, file_path: str) -> bool:
        """Play audio file using available audio backend"""
        try:
            # Try sounddevice first (better quality)
            if SOUNDDEVICE_AVAILABLE:
                try:
                    data, fs = sf.read(file_path)
                    sd.play(data, fs)
                    sd.wait()  # Wait until file is done playing
                    os.unlink(file_path)
                    return True
                except Exception:
                    pass
            
            # Fallback to pygame
            if PYGAME_AVAILABLE:
                try:
                    if not pygame.mixer.get_init():
                        pygame.mixer.init()
                    
                    pygame.mixer.music.load(file_path)
                    pygame.mixer.music.play()
                    
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)
                    
                    pygame.mixer.music.unload()
                    os.unlink(file_path)
                    return True
                except Exception:
                    pass
            
            # Clean up file
            try:
                os.unlink(file_path)
            except:
                pass
                
            return False
            
        except Exception as e:
            logger.error(f"Audio playback error: {e}")
            return False
    
    def stop_speaking(self):
        """Stop current speech"""
        try:
            if PYGAME_AVAILABLE and pygame.mixer.get_init():
                pygame.mixer.music.stop()
            
            if SOUNDDEVICE_AVAILABLE:
                sd.stop()
                
            self.is_speaking = False
            
        except Exception as e:
            logger.error(f"Stop speaking error: {e}")
    
    def get_available_voices(self) -> Dict[str, List[str]]:
        """Get all available voices for each engine"""
        voices = {}
        for engine_name, engine_info in self.engines.items():
            if engine_info['available']:
                voices[engine_name] = engine_info['voices']
        return voices
    
    def set_voice_settings(self, **kwargs):
        """Update voice settings"""
        for key, value in kwargs.items():
            if hasattr(self.config, f"SwarAI_{key.upper()}"):
                setattr(self.config, f"SwarAI_{key.upper()}", value)

# Global TTS instance
conversational_tts = ConversationalTTS()