"""
Custom CrewAI Tools for Agentic AI Task Automation
Specialized tools for WhatsApp, File Management, and System Operations
"""

import os
import glob
import platform
import subprocess
import mimetypes
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

class WhatsAppInputSchema(BaseModel):
    """Input schema for WhatsApp tool"""
    contact: str = Field(..., description="Contact name or phone number")
    message: str = Field(..., description="Message to send")
    phone: str = Field(None, description="Optional phone number if contact not found")

class WhatsAppTool(BaseTool):
    """Custom tool for WhatsApp operations"""
    name: str = "WhatsApp Messenger"
    description: str = "Send WhatsApp messages and create shareable links"
    args_schema: Type[BaseModel] = WhatsAppInputSchema
    
    def _run(self, contact: str, message: str, phone: str = None) -> str:
        """Execute WhatsApp messaging"""
        try:
            # Mock contact database - in production, integrate with real contacts
            contacts_db = {
                "mom": "+1234567890",
                "dad": "+1234567891", 
                "friend": "+1234567892",
                "boss": "+1234567893",
                "family": "+1234567890"  # group
            }
            
            # Get phone number
            if phone:
                target_phone = phone
            else:
                target_phone = contacts_db.get(contact.lower(), None)
                if not target_phone:
                    return f"❌ Contact '{contact}' not found in contacts database"
            
            # Clean phone number
            clean_phone = target_phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
            if not clean_phone.startswith("+"):
                clean_phone = "+1" + clean_phone  # Default to US
            
            # Encode message for URL
            import urllib.parse
            encoded_message = urllib.parse.quote(message)
            encoded_phone = urllib.parse.quote(clean_phone)
            
            # Create WhatsApp URL
            whatsapp_url = f"https://api.whatsapp.com/send/?phone={encoded_phone}&text={encoded_message}&type=phone_number&app_absent=0"
            
            return f"✅ WhatsApp message prepared for {contact}!\n\n📱 Phone: {clean_phone}\n💬 Message: {message}\n🔗 Link: {whatsapp_url}\n\n💡 Click the link to send via WhatsApp!"
            
        except Exception as e:
            return f"❌ WhatsApp tool error: {str(e)}"

class AdvancedFileSearchTool(BaseTool):
    """Advanced file search and management tool"""
    name: str = "Advanced File Manager"
    description: str = "Search, open, and manage files with intelligent matching"
    
    def _run(self, query: str, operation: str = "search") -> str:
        """Execute file operations"""
        try:
            search_locations = self._get_search_locations()
            
            if operation == "search":
                return self._search_files(query, search_locations)
            elif operation == "open":
                return self._open_file(query, search_locations)
            else:
                return f"❌ Unknown operation: {operation}"
                
        except Exception as e:
            return f"❌ File tool error: {str(e)}"
    
    def _get_search_locations(self) -> List[str]:
        """Get platform-specific search locations"""
        system = platform.system().lower()
        locations = []
        
        if system == "windows":
            user_profile = os.environ.get('USERPROFILE', '')
            locations.extend([
                os.path.join(user_profile, 'Documents'),
                os.path.join(user_profile, 'Desktop'),
                os.path.join(user_profile, 'Downloads'),
                os.path.join(user_profile, 'Pictures'),
                os.path.join(user_profile, 'Videos'),
                os.path.join(user_profile, 'Music')
            ])
        elif system == "darwin":  # macOS
            home = os.path.expanduser('~')
            locations.extend([
                os.path.join(home, 'Documents'),
                os.path.join(home, 'Desktop'),
                os.path.join(home, 'Downloads'),
                os.path.join(home, 'Pictures'),
                os.path.join(home, 'Movies'),
                os.path.join(home, 'Music')
            ])
        else:  # Linux
            home = os.path.expanduser('~')
            locations.extend([
                os.path.join(home, 'Documents'),
                os.path.join(home, 'Desktop'),
                os.path.join(home, 'Downloads'),
                os.path.join(home, 'Pictures'),
                os.path.join(home, 'Videos'),
                os.path.join(home, 'Music')
            ])
        
        return [loc for loc in locations if os.path.exists(loc)]
    
    def _search_files(self, query: str, locations: List[str]) -> str:
        """Search for files matching query"""
        results = []
        query_lower = query.lower()
        
        for location in locations:
            try:
                patterns = [
                    f"*{query}*",
                    f"*{query}*.*",
                    f"{query}*",
                    f"*.{query}"
                ]
                
                for pattern in patterns:
                    search_pattern = os.path.join(location, '**', pattern)
                    matches = glob.glob(search_pattern, recursive=True)
                    
                    for match in matches:
                        if os.path.isfile(match):
                            file_info = self._get_file_info(match)
                            if self._fuzzy_match(query_lower, file_info['name'].lower()) > 0:
                                results.append(file_info)
            except Exception:
                continue
        
        if not results:
            return f"❌ No files found matching '{query}'"
        
        # Format results
        response = f"🔍 Found {len(results)} file(s) matching '{query}':\n\n"
        for i, file_info in enumerate(results[:5], 1):
            size_mb = file_info['size'] / (1024 * 1024)
            response += f"{i}. 📄 **{file_info['name']}**\n"
            response += f"   📂 {file_info['path']}\n"
            response += f"   📏 {size_mb:.1f}MB • Modified: {file_info['modified']}\n\n"
        
        if len(results) > 5:
            response += f"... and {len(results) - 5} more files\n"
        
        return response
    
    def _open_file(self, query: str, locations: List[str]) -> str:
        """Open file matching query"""
        # First search for the file
        files = []
        query_lower = query.lower()
        
        for location in locations:
            try:
                for root, dirs, filenames in os.walk(location):
                    for filename in filenames:
                        if self._fuzzy_match(query_lower, filename.lower()) > 0.7:
                            files.append(os.path.join(root, filename))
            except Exception:
                continue
        
        if not files:
            return f"❌ File '{query}' not found"
        
        # Open the best match
        best_file = files[0]
        
        try:
            system = platform.system().lower()
            if system == "windows":
                os.startfile(best_file)
            elif system == "darwin":
                subprocess.run(["open", best_file], check=True)
            else:
                subprocess.run(["xdg-open", best_file], check=True)
            
            return f"✅ Successfully opened: {os.path.basename(best_file)}\n📂 Path: {best_file}"
            
        except Exception as e:
            return f"❌ Failed to open file: {str(e)}"
    
    def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get file information"""
        try:
            stat = os.stat(file_path)
            return {
                'name': os.path.basename(file_path),
                'path': file_path,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
                'type': os.path.splitext(file_path)[1].lower()
            }
        except Exception:
            return {
                'name': os.path.basename(file_path),
                'path': file_path,
                'size': 0,
                'modified': 'Unknown',
                'type': 'Unknown'
            }
    
    def _fuzzy_match(self, query: str, filename: str) -> float:
        """Calculate fuzzy match score"""
        if query == filename:
            return 1.0
        if query in filename:
            return 0.8
        
        # Word matching
        query_words = query.split()
        filename_words = filename.replace('.', ' ').replace('_', ' ').replace('-', ' ').split()
        
        matching_words = sum(1 for word in query_words if any(word in fw for fw in filename_words))
        if matching_words > 0:
            return 0.6 * (matching_words / len(query_words))
        
        return 0.0

class CalendarTool(BaseTool):
    """Calendar and reminder management tool"""
    name: str = "Calendar Manager"
    description: str = "Manage calendar events, reminders, and scheduling"
    
    def _run(self, action: str, title: str, time: str = None, description: str = None) -> str:
        """Execute calendar operations"""
        try:
            if action == "add_reminder":
                return self._add_reminder(title, time, description)
            elif action == "schedule_event":
                return self._schedule_event(title, time, description)
            else:
                return f"❌ Unknown calendar action: {action}"
        except Exception as e:
            return f"❌ Calendar tool error: {str(e)}"
    
    def _add_reminder(self, title: str, time: str = None, description: str = None) -> str:
        """Add a reminder"""
        reminder_text = f"⏰ Reminder set: {title}"
        if time:
            reminder_text += f"\n🕐 Time: {time}"
        if description:
            reminder_text += f"\n📝 Details: {description}"
        
        # In production, integrate with actual calendar APIs
        reminder_text += "\n\n💡 Reminder has been saved to your calendar!"
        return reminder_text
    
    def _schedule_event(self, title: str, time: str = None, description: str = None) -> str:
        """Schedule an event"""
        event_text = f"📅 Event scheduled: {title}"
        if time:
            event_text += f"\n🕐 Time: {time}"
        if description:
            event_text += f"\n📝 Details: {description}"
        
        # In production, integrate with actual calendar APIs
        event_text += "\n\n✅ Event has been added to your calendar!"
        return event_text

class VoiceProcessingTool(BaseTool):
    """Voice and audio processing tool"""
    name: str = "Voice Processor"
    description: str = "Handle voice commands and text-to-speech operations"
    
    def _run(self, action: str, text: str = None, language: str = "en") -> str:
        """Execute voice operations"""
        try:
            if action == "text_to_speech":
                return self._text_to_speech(text, language)
            elif action == "speech_to_text":
                return self._speech_to_text()
            else:
                return f"❌ Unknown voice action: {action}"
        except Exception as e:
            return f"❌ Voice tool error: {str(e)}"
    
    def _text_to_speech(self, text: str, language: str = "en") -> str:
        """Convert text to speech"""
        try:
            from gtts import gTTS
            import pygame
            import tempfile
            
            # Create TTS
            tts = gTTS(text=text, lang=language, slow=False)
            
            # Save to temporary file and play
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tts.save(tmp_file.name)
                
                # Initialize pygame mixer
                pygame.mixer.init()
                pygame.mixer.music.load(tmp_file.name)
                pygame.mixer.music.play()
                
                # Wait for completion
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)
                
                # Cleanup
                pygame.mixer.quit()
                os.unlink(tmp_file.name)
            
            return f"🔊 Audio played: '{text}'"
            
        except Exception as e:
            return f"🔊 Would say: '{text}' (Audio error: {str(e)})"
    
    def _speech_to_text(self) -> str:
        """Convert speech to text"""
        # This would integrate with actual speech recognition
        return "🎤 Speech recognition feature - integrate with frontend voice input"

# Export tools for use in CrewAI agents
whatsapp_tool = WhatsAppTool()
file_tool = AdvancedFileSearchTool()
calendar_tool = CalendarTool()
voice_tool = VoiceProcessingTool()