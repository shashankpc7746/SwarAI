"""
FIXED Screenshot Agent - Uses PIL ImageGrab (Actually Works!)
This version uses Python's PIL library instead of PowerShell for reliable screenshots.
"""

import os
import platform
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, TypedDict, Optional
from langchain.tools import BaseTool
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from pydantic import BaseModel
from config import config

# Try to import PIL - if not available, fallback to subprocess methods
try:
    from PIL import ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("[WARNING] PIL not installed. Screenshot will use fallback methods.")
    print("[FIX] Run: pip install pillow")

class ScreenshotState(TypedDict):
    """State for screenshot workflow"""
    user_input: str
    action_type: str
    screenshot_path: Optional[str]
    screenshot_size: Optional[float]
    response_message: str
    error: Optional[str]

class ScreenshotTool(BaseTool):
    """Tool for capturing screenshots - FIXED VERSION"""
    name: str = "screenshot_capture"
    description: str = "Capture screenshot of the screen"
    
    def _run(self) -> Dict[str, Any]:
        """Capture screenshot - ACTUALLY WORKS NOW!"""
        try:
            # Create screenshots directory
            screenshots_dir = Path.home() / "Pictures" / "Screenshots"
            screenshots_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = screenshots_dir / f"screenshot_{timestamp}.png"
            
            system = platform.system()
            
            # METHOD 1: PIL ImageGrab (BEST - Works on Windows/Mac/Linux with X11)
            if PIL_AVAILABLE:
                print(f"[SCREENSHOT] Using PIL ImageGrab method")
                try:
                    # Capture entire screen
                    screenshot = ImageGrab.grab()
                    
                    # Save as PNG
                    screenshot.save(str(screenshot_path), 'PNG')
                    
                    # Verify file exists
                    if screenshot_path.exists():
                        file_size = screenshot_path.stat().st_size / 1024  # KB
                        return {
                            "success": True,
                            "message": f"✅ Screenshot captured successfully!",
                            "path": str(screenshot_path),
                            "size_kb": round(file_size, 2),
                            "method": "PIL ImageGrab"
                        }
                except Exception as e:
                    print(f"[SCREENSHOT] PIL method failed: {e}")
                    # Fall through to platform-specific methods
            
            # METHOD 2: Platform-specific fallbacks
            import subprocess
            
            if system == "Windows":
                print(f"[SCREENSHOT] Using Windows fallback method")
                # Try PowerShell with better error handling
                ps_script = f'''
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bitmap = New-Object System.Drawing.Bitmap $screen.Width, $screen.Height
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.CopyFromScreen($screen.Location, [System.Drawing.Point]::Empty, $screen.Size)
$bitmap.Save('{screenshot_path}', [System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose()
$bitmap.Dispose()

Write-Output "Screenshot saved"
'''
                result = subprocess.run(
                    ['powershell', '-ExecutionPolicy', 'Bypass', '-Command', ps_script],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                # Check if PowerShell worked
                if screenshot_path.exists():
                    file_size = screenshot_path.stat().st_size / 1024
                    return {
                        "success": True,
                        "message": f"✅ Screenshot captured via PowerShell!",
                        "path": str(screenshot_path),
                        "size_kb": round(file_size, 2),
                        "method": "PowerShell"
                    }
                else:
                    # Last resort: Open Snipping Tool
                    subprocess.Popen(['snippingtool', '/clip'])
                    return {
                        "success": True,
                        "message": "📸 Snipping Tool opened - please capture manually and save",
                        "path": str(screenshots_dir),
                        "manual": True,
                        "method": "Snipping Tool"
                    }
                    
            elif system == "Darwin":  # macOS
                print(f"[SCREENSHOT] Using macOS screencapture")
                subprocess.run(['screencapture', str(screenshot_path)], check=True)
                
            else:  # Linux
                print(f"[SCREENSHOT] Using Linux screenshot tools")
                # Try various Linux tools
                tools = [
                    (['scrot', str(screenshot_path)], 'scrot'),
                    (['gnome-screenshot', '-f', str(screenshot_path)], 'gnome-screenshot'),
                    (['import', '-window', 'root', str(screenshot_path)], 'imagemagick'),
                ]
                
                for cmd, tool_name in tools:
                    try:
                        subprocess.run(cmd, check=True, timeout=5)
                        if screenshot_path.exists():
                            break
                    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                        continue
            
            # Verify screenshot was created
            if screenshot_path.exists():
                file_size = screenshot_path.stat().st_size / 1024  # KB
                return {
                    "success": True,
                    "message": f"✅ Screenshot captured successfully!",
                    "path": str(screenshot_path),
                    "size_kb": round(file_size, 2),
                    "method": f"{system} native"
                }
            else:
                return {
                    "success": False,
                    "message": "❌ Screenshot capture failed. Try: Win+Shift+S or Win+PrintScreen",
                    "path": None,
                    "error": "File not created",
                    "suggestion": "Install PIL: pip install pillow"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Screenshot error: {str(e)}",
                "path": None,
                "error": str(e),
                "suggestion": "Try manual: Win+Shift+S (Windows) or Cmd+Shift+4 (Mac)"
            }

class ScreenshotAgent:
    """Screenshot agent with LangGraph workflow"""
    
    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=config.GROQ_API_KEY,
            model_name=config.GROQ_MODEL,
            temperature=config.AGENT_TEMPERATURE,
            max_tokens=config.MAX_RESPONSE_TOKENS
        )
        
        self.screenshot_tool = ScreenshotTool()
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow"""
        
        def parse_command_node(state: ScreenshotState) -> ScreenshotState:
            """Parse screenshot command"""
            try:
                # Simple parsing - all screenshot commands are captures
                state['action_type'] = 'capture'
                state['error'] = None
            except Exception as e:
                state['error'] = f"Parse error: {str(e)}"
            return state
        
        def capture_screenshot_node(state: ScreenshotState) -> ScreenshotState:
            """Execute screenshot capture"""
            try:
                if state.get('error'):
                    return state
                
                result = self.screenshot_tool._run()
                
                if result['success']:
                    state['screenshot_path'] = result.get('path')
                    state['screenshot_size'] = result.get('size_kb')
                    state['response_message'] = result['message']
                    
                    # Add helpful info
                    if result.get('method'):
                        state['response_message'] += f"\n📍 Location: {result['path']}"
                        if result.get('size_kb'):
                            state['response_message'] += f"\n📊 Size: {result['size_kb']} KB"
                else:
                    state['error'] = result.get('error')
                    state['response_message'] = result['message']
                    if result.get('suggestion'):
                        state['response_message'] += f"\n💡 {result['suggestion']}"
                    
            except Exception as e:
                state['error'] = str(e)
                state['response_message'] = f"❌ Screenshot failed: {str(e)}"
            
            return state
        
        # Build workflow
        workflow = StateGraph(ScreenshotState)
        workflow.add_node("parse_command", parse_command_node)
        workflow.add_node("capture_screenshot", capture_screenshot_node)
        
        workflow.set_entry_point("parse_command")
        workflow.add_edge("parse_command", "capture_screenshot")
        workflow.add_edge("capture_screenshot", END)
        
        return workflow.compile()
    
    def process_command(self, user_input: str) -> Dict[str, Any]:
        """Process screenshot command"""
        try:
            initial_state: ScreenshotState = {
                "user_input": user_input,
                "action_type": "",
                "screenshot_path": None,
                "screenshot_size": None,
                "response_message": "",
                "error": None
            }
            
            result = self.workflow.invoke(initial_state)
            
            return {
                "success": not bool(result.get('error')),
                "message": result.get('response_message', 'Screenshot attempted'),
                "path": result.get('screenshot_path'),
                "size_kb": result.get('screenshot_size'),
                "error": result.get('error')
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Screenshot agent error: {str(e)}",
                "path": None,
                "error": str(e)
            }

# Global instance
screenshot_agent = ScreenshotAgent()

# Print startup info
if PIL_AVAILABLE:
    print("[✅] Screenshot Agent: PIL ImageGrab available - screenshots will work!")
else:
    print("[⚠️] Screenshot Agent: PIL not installed - using fallback methods")
    print("[💡] For best results: pip install pillow")
