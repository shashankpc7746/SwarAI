"""
Phone Agent for AI Task Automation Assistant
Searches contacts and initiates calls via system dialer
"""

import webbrowser
import urllib.parse
import subprocess
import platform
import re
from typing import Dict, Any, Optional, TypedDict, ClassVar
from langchain.tools import BaseTool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from config import config

class PhoneCall(BaseModel):
    """Phone call structure"""
    contact_name: str
    phone_number: Optional[str] = None

class AgentState(TypedDict):
    """State for the Phone agent workflow"""
    user_input: str
    parsed_command: Dict[str, Any]
    contact_info: Dict[str, str]
    call_url: str
    response_message: str
    error: Optional[str]

class ContactSearchTool(BaseTool):
    """Tool to search for contact information"""
    name: str = "contact_search"
    description: str = "Search for contact information given a name"
    
    # Mock contact database - in production, integrate with Windows Contacts or phone API
    mock_contacts: ClassVar[Dict[str, str]] = {
        "vijay": "+919876543211",
        "jay": "+919321781905",
        "principal sir":"+919702011319",
        "mom": "+919876543212",
        "dad": "+919876543213",
        "john": "+919876543214",
        "alice": "+919876543215",
        "boss": "+919876543216",
        "office": "+919876543217",
        "home": "+919876543218"
    }
    
    def _run(self, contact_name: str) -> str:
        """Search for contact by name"""
        name_lower = contact_name.lower().strip()
        if name_lower in self.mock_contacts:
            return self.mock_contacts[name_lower]
        return f"Contact '{contact_name}' not found"

class PhoneDialerTool(BaseTool):
    """Tool to initiate phone calls"""
    name: str = "phone_dialer"
    description: str = "Initiate phone call via system dialer"
    
    def _run(self, phone_number: str, contact_name: str = "") -> str:
        """Initiate phone call"""
        try:
            # Clean phone number
            clean_phone = re.sub(r'[^\d+]', '', phone_number)
            
            # Use tel: protocol (works on Windows with Skype, mobile devices)
            call_url = f"tel:{clean_phone}"
            
            system = platform.system()
            
            if system == "Windows":
                # Windows: Try to open with default tel handler (Skype, etc.)
                try:
                    subprocess.Popen(['cmd', '/c', 'start', call_url], shell=True)
                except:
                    # Fallback: open Skype directly
                    skype_url = f"skype:{clean_phone}?call"
                    subprocess.Popen(['cmd', '/c', 'start', skype_url], shell=True)
            elif system == "Darwin":  # macOS
                subprocess.Popen(['open', call_url])
            else:  # Linux
                subprocess.Popen(['xdg-open', call_url])
            
            contact_info = f" ({contact_name})" if contact_name else ""
            return f"Calling {phone_number}{contact_info}"
            
        except Exception as e:
            return f"Error initiating call: {str(e)}"

class PhoneAgent:
    """LangGraph-powered Phone Agent"""
    
    def __init__(self):
        # Initialize LLM
        self.llm = ChatGroq(
            groq_api_key=config.GROQ_API_KEY,
            model_name=config.GROQ_MODEL,
            temperature=config.AGENT_TEMPERATURE,
            max_tokens=config.MAX_RESPONSE_TOKENS
        )
        
        # Initialize tools
        self.contact_tool = ContactSearchTool()
        self.dialer_tool = PhoneDialerTool()
        self.tools = [self.contact_tool, self.dialer_tool]
        
        # Build LangGraph workflow
        self.workflow = self._build_workflow()
        
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for phone calls"""
        
        def parse_command_node(state: AgentState) -> AgentState:
            """Parse user command to extract contact/phone info"""
            try:
                user_input = state['user_input']
                
                # Extract contact name or phone number
                contact_name = self._extract_contact_name(user_input)
                phone_number = self._extract_phone_number(user_input)
                
                state['parsed_command'] = {
                    "contact_name": contact_name,
                    "phone_number": phone_number
                }
                state['error'] = None
                
            except Exception as e:
                state['error'] = f"Failed to parse phone command: {str(e)}"
                state['parsed_command'] = {}
                
            return state
        
        def search_contact_node(state: AgentState) -> AgentState:
            """Search for contact information"""
            try:
                if state.get('error'):
                    return state
                
                parsed = state['parsed_command']
                contact_name = parsed.get('contact_name', '')
                phone_number = parsed.get('phone_number', '')
                
                # If phone number already provided, skip search
                if phone_number:
                    state['contact_info'] = {
                        "name": contact_name,
                        "number": phone_number
                    }
                else:
                    # Search for contact
                    result = self.contact_tool._run(contact_name)
                    
                    if "not found" in result.lower():
                        state['error'] = f"Contact '{contact_name}' not found in contacts"
                        return state
                    
                    state['contact_info'] = {
                        "name": contact_name,
                        "number": result
                    }
                
                state['error'] = None
                
            except Exception as e:
                state['error'] = f"Failed to search contact: {str(e)}"
                state['contact_info'] = {}
                
            return state
        
        def initiate_call_node(state: AgentState) -> AgentState:
            """Initiate phone call"""
            try:
                if state.get('error'):
                    return state
                
                contact_info = state.get('contact_info', {})
                phone_number = contact_info.get('number', '')
                contact_name = contact_info.get('name', '')
                
                # Initiate call
                result = self.dialer_tool._run(phone_number, contact_name)
                
                state['call_url'] = f"tel:{phone_number}"
                state['response_message'] = f"✅ Calling {contact_name} at {phone_number}"
                state['error'] = None
                
            except Exception as e:
                state['error'] = f"Failed to initiate call: {str(e)}"
                state['response_message'] = "❌ Failed to make call"
                
            return state
        
        # Build workflow graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("parse_command", parse_command_node)
        workflow.add_node("search_contact", search_contact_node)
        workflow.add_node("initiate_call", initiate_call_node)
        
        # Add edges
        workflow.set_entry_point("parse_command")
        workflow.add_edge("parse_command", "search_contact")
        workflow.add_edge("search_contact", "initiate_call")
        workflow.add_edge("initiate_call", END)
        
        return workflow.compile()
    
    def _extract_contact_name(self, text: str) -> str:
        """Extract contact name from text"""
        # Look for patterns like "call vijay", "phone mom"
        patterns = [
            r'(?:call|phone|dial|ring)\s+([A-Za-z\s]+?)(?:\s+at|\s+on|$)',
            r'(?:make\s+a\s+call\s+to)\s+([A-Za-z\s]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(1).strip()
        
        # Fallback: extract name after common verbs
        words = text.split()
        for i, word in enumerate(words):
            if word.lower() in ['call', 'phone', 'dial', 'ring'] and i + 1 < len(words):
                return words[i + 1]
        
        return ""
    
    def _extract_phone_number(self, text: str) -> str:
        """Extract phone number from text"""
        # Look for phone number patterns
        phone_pattern = r'[\+\d][\d\s\-\(\)]{8,}'
        match = re.search(phone_pattern, text)
        if match:
            return re.sub(r'[^\d+]', '', match.group(0))
        return ""
    
    def process_command(self, user_input: str) -> Dict[str, Any]:
        """Process phone command and return result"""
        try:
            initial_state = {
                "user_input": user_input,
                "parsed_command": {},
                "contact_info": {},
                "call_url": "",
                "response_message": "",
                "error": None
            }
            
            # Run workflow
            final_state = self.workflow.invoke(initial_state)
            
            return {
                "success": final_state.get('error') is None,
                "message": final_state.get('response_message', 'Phone call processed'),
                "call_url": final_state.get('call_url', ''),
                "contact": final_state.get('contact_info', {}),
                "details": final_state.get('parsed_command', {})
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Phone agent error: {str(e)}",
                "call_url": "",
                "contact": {},
                "details": {}
            }

# Create global instance
phone_agent = PhoneAgent()
