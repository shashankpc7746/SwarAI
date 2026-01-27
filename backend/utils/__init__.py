"""
Utilities package for AI Task Automation Assistant
Contains helper functions and processors
"""

try:
    from .enhanced_speech_processor import enhanced_speech_processor
    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False
    enhanced_speech_processor = None

__all__ = ["speech_processor", "enhanced_speech_processor", "ENHANCED_AVAILABLE"]