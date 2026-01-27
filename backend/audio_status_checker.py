"""
Audio System Status Checker for AI Task Automation Assistant
Run this to check the status of all audio components
"""

import streamlit as st

def check_audio_system_status():
    """Check and display the status of all audio system components"""
    
    st.title("🔊 Audio System Status Checker")
    st.write("This tool checks the status of all audio components in your AI assistant.")
    
    status_report = {}
    
    # Check basic speech recognition
    try:
        import speech_recognition as sr
        status_report["SpeechRecognition"] = "✅ Available"
        
        # Test microphone access
        try:
            r = sr.Recognizer()
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=0.5)
            status_report["Microphone Access"] = "✅ Working"
        except Exception as e:
            status_report["Microphone Access"] = f"❌ Error: {str(e)}"
            
    except ImportError:
        status_report["SpeechRecognition"] = "❌ Not installed"
    
    # Check Pygame
    try:
        import pygame
        pygame.mixer.init()
        status_report["Pygame Audio"] = "✅ Available"
        pygame.mixer.quit()
    except ImportError:
        status_report["Pygame Audio"] = "❌ Not installed"
    except Exception as e:
        status_report["Pygame Audio"] = f"⚠️ Error: {str(e)}"
    
    # Check gTTS
    try:
        from gtts import gTTS
        status_report["Google TTS"] = "✅ Available"
    except ImportError:
        status_report["Google TTS"] = "❌ Not installed"
    
    # Check Pydub
    try:
        from pydub import AudioSegment
        status_report["Pydub Audio"] = "✅ Available"
        
        # Check FFmpeg
        try:
            AudioSegment.empty()
            status_report["FFmpeg Support"] = "✅ Available"
        except Exception:
            status_report["FFmpeg Support"] = "⚠️ Not available (install FFmpeg for full functionality)"
            
    except ImportError:
        status_report["Pydub Audio"] = "❌ Not installed"
    
    # Check Whisper
    try:
        import whisper
        status_report["Whisper AI"] = "✅ Available (may show warnings on first load)"
    except ImportError:
        status_report["Whisper AI"] = "❌ Not installed"
    
    # Check Enhanced Speech Processor
    try:
        from utils.enhanced_speech_processor import enhanced_speech_processor
        status_report["Enhanced Speech Processor"] = "✅ Available"
    except ImportError:
        status_report["Enhanced Speech Processor"] = "❌ Import failed"
    except Exception as e:
        status_report["Enhanced Speech Processor"] = f"⚠️ Error: {str(e)}"
    
    # Display results
    st.markdown("### 📊 System Status Report")
    
    for component, status in status_report.items():
        if "✅" in status:
            st.success(f"**{component}**: {status}")
        elif "⚠️" in status:
            st.warning(f"**{component}**: {status}")
        else:
            st.error(f"**{component}**: {status}")
    
    # Overall assessment
    working_count = sum(1 for status in status_report.values() if "✅" in status)
    total_count = len(status_report)
    
    st.markdown("---")
    st.markdown("### 🎯 Overall Assessment")
    
    if working_count >= 6:
        st.success(f"🎉 Excellent! {working_count}/{total_count} components working. Your system is fully optimized!")
    elif working_count >= 4:
        st.info(f"👍 Good! {working_count}/{total_count} components working. Core functionality available.")
    else:
        st.warning(f"⚠️ Limited functionality. Only {working_count}/{total_count} components working.")
    
    # Recommendations
    st.markdown("### 💡 Recommendations")
    
    if "❌" in status_report.get("FFmpeg Support", ""):
        st.info("🔧 **Install FFmpeg** to eliminate pydub warnings and enable advanced audio processing.")
    
    if "❌" in status_report.get("Whisper AI", ""):
        st.info("🤖 **Install Whisper** for enhanced speech recognition: `pip install openai-whisper`")
    
    if "❌" in status_report.get("Microphone Access", ""):
        st.error("🎤 **Microphone issues detected**. Check permissions and ensure no other apps are using the microphone.")
    
    return status_report

if __name__ == "__main__":
    check_audio_system_status()
else:
    check_audio_system_status()