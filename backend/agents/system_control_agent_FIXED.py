"""
FIXED System Control Agent - Actually Controls Windows Volume!
This version uses Python libraries instead of unreliable subprocess commands.
"""

import os
import platform
import subprocess
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
