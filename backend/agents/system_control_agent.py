"""
FIXED System Control Agent - Actually Controls Windows Volume!
This version uses Python libraries instead of unreliable subprocess commands.
"""

import os
import platform
import subprocess
from datetime import datetime
from typing import Dict, Any, Optional, TypedDict, ClassVar
from langchain.tools import BaseTool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from pydantic import BaseModel
from config import config

# Try to import pycaw for Windows volume control
try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    PYCAW_AVAILABLE = True
except ImportError:
    PYCAW_AVAILABLE = False
    print("[WARNING] pycaw not installed. Volume control will use fallback methods.")
    print("[FIX] Run: pip install pycaw comtypes")

# Try to import psutil for battery info
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("[WARNING] psutil not installed. Battery info will not be available.")
    print("[FIX] Run: pip install psutil")

# Try to import screen_brightness_control for brightness
try:
    import screen_brightness_control as sbc
    SBC_AVAILABLE = True
except ImportError:
    SBC_AVAILABLE = False
    print("[WARNING] screen-brightness-control not installed. Brightness control will not be available.")
    print("[FIX] Run: pip install screen-brightness-control")

class SystemState(TypedDict):
    """State for the System Control agent workflow"""
    user_input: str
    action_type: str
    action_value: Optional[str]
    response_message: str
    error: Optional[str]

class SystemControlTool(BaseTool):
    """Tool for system control operations - FIXED VERSION"""
    name: str = "system_control"
    description: str = "Control system settings and operations"
    
    def _run(self, action: str, value: str = None) -> Dict[str, Any]:
        """Execute system control action - ACTUALLY WORKS NOW!"""
        try:
            system = platform.system()
            
            # VOLUME CONTROL - FIXED for Windows
            if action in ["volume_up", "volume_down", "mute", "unmute"]:
                if system == "Windows":
                    return self._windows_volume_control(action)
                elif system == "Darwin":
                    return self._macos_volume_control(action)
                else:
                    return self._linux_volume_control(action)
            
            # BRIGHTNESS CONTROL
            elif action in ["brightness_up", "brightness_down", "set_brightness"]:
                return self._brightness_control(action, value)
            
            # SYSTEM INFO
            elif action == "battery":
                return self._get_battery_info()
            
            elif action == "time":
                return self._get_current_time()
            
            # LOCK SCREEN
            elif action == "lock":
                return self._lock_screen(system)
            
            # POWER OPERATIONS
            elif action in ["shutdown", "restart", "sleep"]:
                return self._power_operation(system, action)
            
            else:
                return {
                    "success": False,
                    "message": f"Unknown action: {action}",
                    "error": "Unknown action"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to execute {action}: {str(e)}",
                "error": str(e)
            }
    
    def _windows_volume_control(self, action: str) -> Dict[str, Any]:
        """Windows volume control - FIXED VERSION"""
        try:
            if PYCAW_AVAILABLE:
                # Use pycaw - ACTUALLY WORKS!
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                
                if action == "volume_up":
                    current = volume.GetMasterVolumeLevelScalar()
                    new_volume = min(1.0, current + 0.1)  # +10%
                    volume.SetMasterVolumeLevelScalar(new_volume, None)
                    percent = int(new_volume * 100)
                    return {
                        "success": True,
                        "message": f"✅ Volume increased to {percent}%",
                        "action": action,
                        "method": "pycaw"
                    }
                
                elif action == "volume_down":
                    current = volume.GetMasterVolumeLevelScalar()
                    new_volume = max(0.0, current - 0.1)  # -10%
                    volume.SetMasterVolumeLevelScalar(new_volume, None)
                    percent = int(new_volume * 100)
                    return {
                        "success": True,
                        "message": f"✅ Volume decreased to {percent}%",
                        "action": action,
                        "method": "pycaw"
                    }
                
                elif action == "mute":
                    volume.SetMute(1, None)
                    return {
                        "success": True,
                        "message": "✅ System muted",
                        "action": action,
                        "method": "pycaw"
                    }
                
                elif action == "unmute":
                    volume.SetMute(0, None)
                    return {
                        "success": True,
                        "message": "✅ System unmuted",
                        "action": action,
                        "method": "pycaw"
                    }
            
            else:
                # Fallback: Try nircmd if available
                nircmd_path = "nircmd.exe"  # Assumes in PATH or System32
                
                commands = {
                    "volume_up": [nircmd_path, "changesysvolume", "5000"],
                    "volume_down": [nircmd_path, "changesysvolume", "-5000"],
                    "mute": [nircmd_path, "mutesysvolume", "1"],
                    "unmute": [nircmd_path, "mutesysvolume", "0"]
                }
                
                try:
                    subprocess.run(commands[action], check=True, timeout=2)
                    return {
                        "success": True,
                        "message": f"✅ {action.replace('_', ' ').title()} executed (nircmd)",
                        "action": action,
                        "method": "nircmd"
                    }
                except (FileNotFoundError, subprocess.CalledProcessError):
                    return {
                        "success": False,
                        "message": f"❌ Volume control not available",
                        "error": "pycaw not installed and nircmd not found",
                        "suggestion": "Install pycaw: pip install pycaw comtypes"
                    }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Windows volume control failed: {str(e)}",
                "error": str(e)
            }
    
    def _macos_volume_control(self, action: str) -> Dict[str, Any]:
        """macOS volume control"""
        try:
            commands = {
                "volume_up": "osascript -e 'set volume output volume (output volume of (get volume settings) + 10)'",
                "volume_down": "osascript -e 'set volume output volume (output volume of (get volume settings) - 10)'",
                "mute": "osascript -e 'set volume output muted true'",
                "unmute": "osascript -e 'set volume output muted false'"
            }
            
            subprocess.run(commands[action], shell=True, check=True)
            return {
                "success": True,
                "message": f"✅ {action.replace('_', ' ').title()} executed",
                "action": action
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ macOS volume control failed: {str(e)}",
                "error": str(e)
            }
    
    def _linux_volume_control(self, action: str) -> Dict[str, Any]:
        """Linux volume control"""
        try:
            commands = {
                "volume_up": "amixer -D pulse sset Master 10%+",
                "volume_down": "amixer -D pulse sset Master 10%-",
                "mute": "amixer -D pulse sset Master mute",
                "unmute": "amixer -D pulse sset Master unmute"
            }
            
            subprocess.run(commands[action], shell=True, check=True)
            return {
                "success": True,
                "message": f"✅ {action.replace('_', ' ').title()} executed",
                "action": action
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Linux volume control failed: {str(e)}",
                "error": str(e)
            }
    
    def _lock_screen(self, system: str) -> Dict[str, Any]:
        """Lock screen - cross-platform"""
        try:
            commands = {
                "Windows": "rundll32.exe user32.dll,LockWorkStation",
                "Darwin": "pmset displaysleepnow",
                "Linux": "xdg-screensaver lock"
            }
            
            subprocess.Popen(commands[system], shell=True)
            return {
                "success": True,
                "message": "✅ Screen locked",
                "action": "lock"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Lock screen failed: {str(e)}",
                "error": str(e)
            }
    
    def _power_operation(self, system: str, action: str) -> Dict[str, Any]:
        """Power operations (shutdown, restart, sleep)"""
        try:
            commands = {
                "Windows": {
                    "shutdown": "shutdown /s /t 10",
                    "restart": "shutdown /r /t 10",
                    "sleep": "rundll32.exe powrprof.dll,SetSuspendState 0,1,0"
                },
                "Darwin": {
                    "shutdown": "shutdown -h +1",
                    "restart": "shutdown -r +1",
                    "sleep": "pmset sleepnow"
                },
                "Linux": {
                    "shutdown": "shutdown -h +1",
                    "restart": "shutdown -r +1",
                    "sleep": "systemctl suspend"
                }
            }
            
            subprocess.Popen(commands[system][action], shell=True)
            
            messages = {
                "shutdown": "✅ Shutdown initiated (10 seconds)",
                "restart": "✅ Restart initiated (10 seconds)",
                "sleep": "✅ Sleep mode activated"
            }
            
            return {
                "success": True,
                "message": messages[action],
                "action": action
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Power operation failed: {str(e)}",
                "error": str(e)
            }
    
    def _brightness_control(self, action: str, value: str = None) -> Dict[str, Any]:
        """Control screen brightness"""
        try:
            if not SBC_AVAILABLE:
                return {
                    "success": False,
                    "message": "❌ Brightness control not available",
                    "error": "screen-brightness-control not installed",
                    "suggestion": "Install: pip install screen-brightness-control"
                }
            
            if action == "brightness_up":
                current = sbc.get_brightness()[0]  # Get first monitor
                new_brightness = min(100, current + 10)
                sbc.set_brightness(new_brightness)
                return {
                    "success": True,
                    "message": f"✅ Brightness increased to {new_brightness}%",
                    "action": action,
                    "brightness": new_brightness
                }
            
            elif action == "brightness_down":
                current = sbc.get_brightness()[0]
                new_brightness = max(0, current - 10)
                sbc.set_brightness(new_brightness)
                return {
                    "success": True,
                    "message": f"✅ Brightness decreased to {new_brightness}%",
                    "action": action,
                    "brightness": new_brightness
                }
            
            elif action == "set_brightness" and value:
                brightness_value = int(value)
                brightness_value = max(0, min(100, brightness_value))  # Clamp 0-100
                sbc.set_brightness(brightness_value)
                return {
                    "success": True,
                    "message": f"✅ Brightness set to {brightness_value}%",
                    "action": action,
                    "brightness": brightness_value
                }
            
            else:
                return {
                    "success": False,
                    "message": "❌ Invalid brightness action",
                    "error": "Invalid action or missing value"
                }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Brightness control failed: {str(e)}",
                "error": str(e)
            }
    
    def _get_battery_info(self) -> Dict[str, Any]:
        """Get battery information"""
        try:
            if not PSUTIL_AVAILABLE:
                return {
                    "success": False,
                    "message": "❌ Battery info not available",
                    "error": "psutil not installed",
                    "suggestion": "Install: pip install psutil"
                }
            
            battery = psutil.sensors_battery()
            
            if battery is None:
                return {
                    "success": False,
                    "message": "❌ No battery detected (desktop PC?)",
                    "error": "No battery sensor found"
                }
            
            percent = battery.percent
            plugged = battery.power_plugged
            time_left = battery.secsleft
            
            # Format message
            status = "Charging" if plugged else "Discharging"
            if time_left == -1:
                time_str = "calculating..."
            elif time_left == -2:
                time_str = "unlimited (plugged in)"
            else:
                hours = time_left // 3600
                minutes = (time_left % 3600) // 60
                time_str = f"{hours}h {minutes}m remaining"
            
            message = f"🔋 Battery: {percent}% ({status})\n⏱️ {time_str}"
            
            return {
                "success": True,
                "message": message,
                "action": "battery",
                "battery_percent": percent,
                "plugged": plugged,
                "time_remaining": time_left
            }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Battery info failed: {str(e)}",
                "error": str(e)
            }
    
    def _get_current_time(self) -> Dict[str, Any]:
        """Get current date and time"""
        try:
            now = datetime.now()
            
            # Format date and time
            date_str = now.strftime("%A, %B %d, %Y")  # Monday, January 01, 2024
            time_str = now.strftime("%I:%M %p")  # 02:30 PM
            
            message = f"🕒 Current time: {time_str}\n📅 Date: {date_str}"
            
            return {
                "success": True,
                "message": message,
                "action": "time",
                "time": time_str,
                "date": date_str,
                "timestamp": now.isoformat()
            }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Get time failed: {str(e)}",
                "error": str(e)
            }

class SystemControlAgent:
    """System Control Agent with LangGraph workflow"""
    
    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=config.GROQ_API_KEY,
            model_name=config.GROQ_MODEL,
            temperature=config.AGENT_TEMPERATURE,
            max_tokens=config.MAX_RESPONSE_TOKENS
        )
        
        self.system_tool = SystemControlTool()
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow"""
        
        def parse_command_node(state: SystemState) -> SystemState:
            """Parse system control command"""
            try:
                user_input = state['user_input'].lower()
                
                # Map user input to actions
                action_mapping = {
                    # Volume controls
                    "volume up": "volume_up",
                    "increase volume": "volume_up",
                    "louder": "volume_up",
                    "raise volume": "volume_up",
                    "volume down": "volume_down",
                    "decrease volume": "volume_down",
                    "quieter": "volume_down",
                    "lower volume": "volume_down",
                    "mute": "mute",
                    "unmute": "unmute",
                    
                    # Brightness controls
                    "brightness up": "brightness_up",
                    "increase brightness": "brightness_up",
                    "brighter": "brightness_up",
                    "brightness down": "brightness_down",
                    "decrease brightness": "brightness_down",
                    "dimmer": "brightness_down",
                    "dim": "brightness_down",
                    
                    # System info
                    "battery": "battery",
                    "battery status": "battery",
                    "battery level": "battery",
                    "battery percentage": "battery",
                    "time": "time",
                    "what time": "time",
                    "current time": "time",
                    "what's the time": "time",
                    "tell me the time": "time",
                    
                    # Lock and power
                    "lock": "lock",
                    "lock screen": "lock",
                    "lock computer": "lock",
                    "shutdown": "shutdown",
                    "shut down": "shutdown",
                    "turn off": "shutdown",
                    "restart": "restart",
                    "reboot": "restart",
                    "sleep": "sleep",
                    "hibernate": "sleep"
                }
                
                # Find matching action
                detected_action = None
                for phrase, action in action_mapping.items():
                    if phrase in user_input:
                        detected_action = action
                        break
                
                if detected_action:
                    state['action_type'] = detected_action
                    state['action_value'] = None
                    state['error'] = None
                else:
                    state['error'] = "Could not identify system action"
                
            except Exception as e:
                state['error'] = f"Failed to parse command: {str(e)}"
            
            return state
        
        def execute_action_node(state: SystemState) -> SystemState:
            """Execute the system action"""
            try:
                if state.get('error'):
                    return state
                
                action = state.get('action_type')
                value = state.get('action_value')
                
                result = self.system_tool._run(action, value)
                
                if result['success']:
                    state['response_message'] = result['message']
                    if result.get('method'):
                        state['response_message'] += f"\n🔧 Method: {result['method']}"
                else:
                    state['error'] = result.get('error')
                    state['response_message'] = result['message']
                    if result.get('suggestion'):
                        state['response_message'] += f"\n💡 {result['suggestion']}"
                
            except Exception as e:
                state['error'] = str(e)
                state['response_message'] = f"❌ Failed to execute system action"
            
            return state
        
        # Build workflow
        workflow = StateGraph(SystemState)
        workflow.add_node("parse_command", parse_command_node)
        workflow.add_node("execute_action", execute_action_node)
        
        workflow.set_entry_point("parse_command")
        workflow.add_edge("parse_command", "execute_action")
        workflow.add_edge("execute_action", END)
        
        return workflow.compile()
    
    def process_command(self, user_input: str) -> Dict[str, Any]:
        """Process system control command"""
        try:
            initial_state: SystemState = {
                "user_input": user_input,
                "action_type": "",
                "action_value": None,
                "response_message": "",
                "error": None
            }
            
            result = self.workflow.invoke(initial_state)
            
            return {
                "success": not bool(result.get('error')),
                "message": result.get('response_message', 'System action completed'),
                "action_type": result.get('action_type'),
                "error": result.get('error')
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ System control error: {str(e)}",
                "action_type": "error",
                "error": str(e)
            }

# Global agent instance
system_control_agent = SystemControlAgent()

# Print startup info
if PYCAW_AVAILABLE:
    print("[✅] System Control Agent: pycaw available - volume control will work!")
else:
    print("[⚠️] System Control Agent: pycaw not installed - volume control may not work")
    print("[💡] For best results: pip install pycaw comtypes")
