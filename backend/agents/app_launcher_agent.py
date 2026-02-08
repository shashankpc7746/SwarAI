"""
Application Launcher Agent for AI Task Automation Assistant
Opens applications, browsers, and websites via voice command
"""

import webbrowser
import subprocess
import platform
import os
import re
from typing import Dict, Any, Optional, TypedDict, ClassVar
from langchain.tools import BaseTool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from config import config

class AppLaunchRequest(BaseModel):
    """Application launch request structure"""
    app_name: str
    app_type: str = "application"  # application, browser, website
    url: Optional[str] = None

class AgentState(TypedDict):
    """State for the App Launcher agent workflow"""
    user_input: str
    parsed_command: Dict[str, Any]
    launch_result: str
    response_message: str
    error: Optional[str]

class AppLauncherTool(BaseTool):
    """Tool to launch applications and open websites"""
    name: str = "app_launcher"
    description: str = "Launch applications, browsers, or open websites"
    
    # Common application paths and commands
    WINDOWS_APPS: ClassVar[Dict[str, str]] = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "paint": "mspaint.exe",
        "wordpad": "write.exe",
        "explorer": "explorer.exe",
        "cmd": "cmd.exe",
        "powershell": "powershell.exe",
        "settings": "ms-settings:",
        "copilot": "microsoft-edge:///?ux=copilot&tcp=1&source=taskbar",
        "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
        "edge": "msedge.exe",
        "opera": r"C:\Users\{username}\AppData\Local\Programs\Opera\opera.exe",
        "brave": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        "word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
        "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
        "powerpoint": r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
        "outlook": r"C:\Program Files\Microsoft Office\root\Office16\OUTLOOK.EXE",
        "vscode": r"C:\Users\{username}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
        "spotify": r"C:\Users\{username}\AppData\Roaming\Spotify\Spotify.exe",
        "discord": r"C:\Users\{username}\AppData\Local\Discord\app-*\Discord.exe",
        "skype": r"C:\Program Files\Microsoft\Skype for Desktop\Skype.exe",
        "teams": r"C:\Users\{username}\AppData\Local\Microsoft\Teams\current\Teams.exe",
        "zoom": r"C:\Users\{username}\AppData\Roaming\Zoom\bin\Zoom.exe",
    }
    
    # Popular websites
    WEBSITES: ClassVar[Dict[str, str]] = {
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "gmail": "https://mail.google.com",
        "github": "https://www.github.com",
        "stackoverflow": "https://stackoverflow.com",
        "linkedin": "https://www.linkedin.com",
        "facebook": "https://www.facebook.com",
        "twitter": "https://www.twitter.com",
        "instagram": "https://www.instagram.com",
        "chatgpt": "https://chat.openai.com",
        "claude": "https://claude.ai",
        "netflix": "https://www.netflix.com",
        "amazon": "https://www.amazon.com",
        "wikipedia": "https://www.wikipedia.org",
    }
    
    def _run(self, app_name: str, app_type: str = "application", url: str = None) -> str:
        """Launch application or open website"""
        try:
            app_name_lower = app_name.lower()
            system = platform.system()
            
            if app_type == "website" or url:
                return self._open_website(url or app_name_lower)
            elif app_type == "browser":
                return self._open_browser(app_name_lower)
            else:
                return self._launch_application(app_name_lower, system)
                
        except Exception as e:
            return f"Error launching {app_name}: {str(e)}"
    
    def _open_website(self, url_or_name: str) -> str:
        """Open website in default browser"""
        # Check if it's a known website shortcut
        if url_or_name in self.WEBSITES:
            url = self.WEBSITES[url_or_name]
        elif not url_or_name.startswith(('http://', 'https://')):
            url = f"https://www.{url_or_name}.com"
        else:
            url = url_or_name
        
        webbrowser.open(url)
        return f"Opened {url} in browser"
    
    def _open_browser(self, browser_name: str) -> str:
        """Open specific browser"""
        browser_map = {
            "chrome": webbrowser.Chrome,
            "firefox": webbrowser.Firefox,
            "edge": webbrowser.Edge,
        }
        
        if browser_name in browser_map:
            webbrowser.get(browser_name).open("about:blank")
        else:
            webbrowser.open("about:blank")
        
        return f"Opened {browser_name} browser"
    
    def _launch_application(self, app_name: str, system: str) -> str:
        """Launch desktop application"""
        if system == "Windows":
            return self._launch_windows_app(app_name)
        elif system == "Darwin":  # macOS
            return self._launch_macos_app(app_name)
        else:  # Linux
            return self._launch_linux_app(app_name)
    
    def _launch_windows_app(self, app_name: str) -> str:
        """Launch application on Windows"""
        username = os.getenv('USERNAME', 'User')
        
        # Check known apps
        if app_name in self.WINDOWS_APPS:
            app_path = self.WINDOWS_APPS[app_name].replace('{username}', username)
            
            # Handle special URI schemes (Settings, Copilot, etc.)
            if app_path.startswith(('ms-', 'microsoft-edge://')):
                try:
                    # Use start command for URI schemes
                    if app_name == 'copilot':
                        # Open Copilot via Edge
                        subprocess.Popen(['start', 'msedge', '--app=' + app_path], shell=True)
                    else:
                        subprocess.Popen(['start', app_path], shell=True)
                    return f"Launched {app_name}"
                except Exception as e:
                    print(f"[APP_LAUNCHER] Failed to launch {app_name} via URI: {e}")
                    return f"Failed to launch {app_name}"
            
            # Handle wildcard paths (like Discord with version numbers)
            if '*' in app_path:
                import glob
                matches = glob.glob(app_path)
                if matches:
                    app_path = matches[0]
            
            try:
                if os.path.exists(app_path):
                    subprocess.Popen([app_path])
                    return f"Launched {app_name}"
                else:
                    # Try using start command
                    subprocess.Popen(['cmd', '/c', 'start', '', app_name], shell=True)
                    return f"Launched {app_name}"
            except Exception as e:
                print(f"[APP_LAUNCHER] Error launching {app_name}: {e}")
                # Fallback to simple command
                try:
                    subprocess.Popen(['start', '', app_name], shell=True)
                    return f"Launched {app_name}"
                except:
                    return f"Failed to launch {app_name}"
        else:
            # Try to launch by name using Windows start command
            # This handles many built-in Windows apps and installed programs
            try:
                subprocess.Popen(['cmd', '/c', 'start', '', app_name], shell=True)
                return f"Launched {app_name}"
            except Exception as e:
                print(f"[APP_LAUNCHER] Failed to launch {app_name}: {e}")
                return f"Could not find or launch {app_name}"
    
    def _launch_macos_app(self, app_name: str) -> str:
        """Launch application on macOS"""
        subprocess.Popen(['open', '-a', app_name])
        return f"Launched {app_name}"
    
    def _launch_linux_app(self, app_name: str) -> str:
        """Launch application on Linux"""
        subprocess.Popen([app_name])
        return f"Launched {app_name}"

class AppLauncherAgent:
    """LangGraph-powered Application Launcher Agent"""
    
    def __init__(self):
        # Initialize LLM
        self.llm = ChatGroq(
            groq_api_key=config.GROQ_API_KEY,
            model_name=config.GROQ_MODEL,
            temperature=config.AGENT_TEMPERATURE,
            max_tokens=config.MAX_RESPONSE_TOKENS
        )
        
        # Initialize tools
        self.launcher_tool = AppLauncherTool()
        self.tools = [self.launcher_tool]
        
        # Build LangGraph workflow
        self.workflow = self._build_workflow()
        
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for app launching"""
        
        def parse_command_node(state: AgentState) -> AgentState:
            """Parse user command to extract app/website info"""
            try:
                user_input = state['user_input']
                
                # Determine app type and name
                app_name, app_type, url = self._parse_launch_request(user_input)
                
                state['parsed_command'] = {
                    "app_name": app_name,
                    "app_type": app_type,
                    "url": url
                }
                state['error'] = None
                
            except Exception as e:
                state['error'] = f"Failed to parse launch command: {str(e)}"
                state['parsed_command'] = {}
                
            return state
        
        def launch_app_node(state: AgentState) -> AgentState:
            """Launch the application or open website"""
            try:
                if state.get('error'):
                    return state
                
                parsed = state['parsed_command']
                app_name = parsed.get('app_name', '')
                app_type = parsed.get('app_type', 'application')
                url = parsed.get('url')
                
                # Launch app
                result = self.launcher_tool._run(app_name, app_type, url)
                
                state['launch_result'] = result
                state['response_message'] = f"✅ {result}"
                state['error'] = None
                
            except Exception as e:
                state['error'] = f"Failed to launch app: {str(e)}"
                state['response_message'] = "❌ Failed to launch"
                
            return state
        
        # Build workflow graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("parse_command", parse_command_node)
        workflow.add_node("launch_app", launch_app_node)
        
        # Add edges
        workflow.set_entry_point("parse_command")
        workflow.add_edge("parse_command", "launch_app")
        workflow.add_edge("launch_app", END)
        
        return workflow.compile()
    
    def _parse_launch_request(self, text: str) -> tuple:
        """Parse launch request to determine app name, type, and URL"""
        text_lower = text.lower()
        
        # Check for website patterns
        website_keywords = ["open", "goto", "visit", "browse", "search"]
        website_names = ["google", "youtube", "gmail", "github", "chatgpt", "claude", "netflix", "amazon"]
        
        if any(keyword in text_lower for keyword in website_keywords) and any(site in text_lower for site in website_names):
            for site in website_names:
                if site in text_lower:
                    return (site, "website", None)
        
        # Check for URL patterns
        if "http://" in text_lower or "https://" in text_lower or ".com" in text_lower or ".org" in text_lower:
            url_match = re.search(r'(https?://[^\s]+|www\.[^\s]+|[a-z0-9-]+\.[a-z]{2,})', text_lower)
            if url_match:
                return (url_match.group(0), "website", url_match.group(0))
        
        # Check for browser launch
        if any(browser in text_lower for browser in ["chrome", "firefox", "edge", "browser"]):
            for browser in ["chrome", "firefox", "edge"]:
                if browser in text_lower:
                    return (browser, "browser", None)
        
        # Application launch patterns
        app_patterns = [
            r'(?:open|launch|start|run)\s+([a-z\s]+)',
            r'([a-z]+)\s+application',
        ]
        
        for pattern in app_patterns:
            match = re.search(pattern, text_lower)
            if match:
                app_name = match.group(1).strip()
                return (app_name, "application", None)
        
        # Fallback: extract first word after action verb
        words = text_lower.split()
        for i, word in enumerate(words):
            if word in ["open", "launch", "start", "run"] and i + 1 < len(words):
                return (words[i + 1], "application", None)
        
        return ("", "application", None)
    
    def process_command(self, user_input: str) -> Dict[str, Any]:
        """Process app launch command and return result"""
        try:
            initial_state = {
                "user_input": user_input,
                "parsed_command": {},
                "launch_result": "",
                "response_message": "",
                "error": None
            }
            
            # Run workflow
            final_state = self.workflow.invoke(initial_state)
            
            return {
                "success": final_state.get('error') is None,
                "message": final_state.get('response_message', 'App launch processed'),
                "launch_result": final_state.get('launch_result', ''),
                "details": final_state.get('parsed_command', {})
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"App launcher error: {str(e)}",
                "launch_result": "",
                "details": {}
            }

# Create global instance
app_launcher_agent = AppLauncherAgent()
