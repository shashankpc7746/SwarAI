"""
WhatsApp Agent for AI Task Automation Assistant
Uses LangGraph for stateful workflow management
"""

import re
import urllib.parse
from typing import Dict, List, Any, Optional, TypedDict, ClassVar
from langchain.tools import BaseTool
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
# ToolExecutor not needed - using direct tool calls
from pydantic import BaseModel, Field
from config import config

class WhatsAppMessage(BaseModel):
    """WhatsApp message structure"""
    recipient: str
    message: str
    phone_number: Optional[str] = None

class AgentState(TypedDict):
    """State for the WhatsApp agent workflow"""
    user_input: str
    parsed_command: Dict[str, Any]
    contact_info: Dict[str, str]
    whatsapp_url: str
    response_message: str
    error: Optional[str]

class ContactSearchTool(BaseTool):
    """Tool to search for contact information"""
    name: str = "contact_search"
    description: str = "Search for contact information given a name"
    
    # Mock contact database - in real implementation, this would connect to actual contacts
    mock_contacts: ClassVar[Dict[str, str]] = {
        "jay": "+919321781905",
        "vijay": "+919876543211", 
        "mom": "+919876543212",
        "dad": "+919876543213",
        "john": "+919876543214",
        "alice": "+919876543215",
        "boss": "+919876543216"
    }
    
    def _run(self, contact_name: str) -> str:
        """Search for contact by name"""
        name_lower = contact_name.lower().strip()
        if name_lower in self.mock_contacts:
            return self.mock_contacts[name_lower]
        return f"Contact '{contact_name}' not found"

class WhatsAppURLTool(BaseTool):
    """Tool to generate WhatsApp wa.me URLs"""
    name: str = "whatsapp_url_generator"
    description: str = "Generate WhatsApp wa.me URL for sending messages"
    
    def _run(self, phone_number: str, message: str) -> str:
        """Generate WhatsApp URL"""
        # Clean phone number (remove spaces, dashes, etc.)
        clean_phone = re.sub(r'[^\d+]', '', phone_number)
        
        # URL encode the message
        encoded_message = urllib.parse.quote(message)
        
        # Generate wa.me URL
        whatsapp_url = f"https://wa.me/{clean_phone}?text={encoded_message}"
        
        return whatsapp_url

class WhatsAppAgent:
    """LangGraph-powered WhatsApp Agent"""
    
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
        self.whatsapp_tool = WhatsAppURLTool()
        self.tools = [self.contact_tool, self.whatsapp_tool]
        
        # Build LangGraph workflow
        self.workflow = self._build_workflow()
        
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for WhatsApp message sending"""
        
        def parse_command_node(state: AgentState) -> AgentState:
            """Parse user command to extract recipient and message"""
            try:
                # Initialize default values if not present
                if 'parsed_command' not in state:
                    state['parsed_command'] = {}
                if 'error' not in state:
                    state['error'] = None
                    
                user_input = state['user_input'].strip()
                
                # First try regex-based parsing for common patterns
                import re
                
                # Pattern 1: "[Send] WhatsApp [message] to [name] [rest of message]"
                pattern1 = r'(?:send\s+)?whatsapp\s+(?:message\s+)?to\s+(\w+)\s+(.+)'
                match1 = re.search(pattern1, user_input, re.IGNORECASE)
                
                # Pattern 2: "[Send] WhatsApp to [name]: [message]"
                pattern2 = r'(?:send\s+)?whatsapp\s+to\s+(\w+)\s*:\s*(.+)'
                match2 = re.search(pattern2, user_input, re.IGNORECASE)
                
                # Pattern 3: "Send WhatsApp message to [name] [message]" (more specific)
                pattern3 = r'send\s+whatsapp\s+message\s+to\s+(\w+)\s+(.+)'
                match3 = re.search(pattern3, user_input, re.IGNORECASE)
                
                # Pattern 4: "Message [name] [message]"
                pattern4 = r'(?:send\s+)?message\s+(\w+)\s+(.+)'
                match4 = re.search(pattern4, user_input, re.IGNORECASE)
                
                # Pattern 5: "Text [name] [message]"
                pattern5 = r'(?:send\s+)?text\s+(\w+)\s+(.+)'
                match5 = re.search(pattern5, user_input, re.IGNORECASE)
                
                recipient = None
                message = None
                
                # Check patterns in order of specificity
                if match3:  # Most specific first
                    recipient, message = match3.groups()
                    print(f"[DEBUG] Pattern 3 match: {recipient} -> {message}")
                elif match2:
                    recipient, message = match2.groups()
                    print(f"[DEBUG] Pattern 2 match: {recipient} -> {message}")
                elif match1:
                    recipient, message = match1.groups()
                    print(f"[DEBUG] Pattern 1 match: {recipient} -> {message}")
                elif match4:
                    recipient, message = match4.groups()
                    print(f"[DEBUG] Pattern 4 match: {recipient} -> {message}")
                elif match5:
                    recipient, message = match5.groups()
                    print(f"[DEBUG] Pattern 5 match: {recipient} -> {message}")
                
                if recipient and message:
                    state['parsed_command'] = {
                        "recipient": recipient.strip(),
                        "message": message.strip()
                    }
                    print(f"[DEBUG] Regex parsing success: {recipient} -> {message}")
                    return state
                
                print(f"[DEBUG] Regex parsing failed, trying LLM parsing...")
                
                # Fallback to LLM parsing
                system_prompt = """You are a command parser for WhatsApp messages. 
                Extract the recipient name and message from user input.
                
                Handle these patterns flexibly:
                - "Send WhatsApp to Jay: Hello how are you" -> recipient: "Jay", message: "Hello how are you"
                - "Message Vijay on WhatsApp: Meeting at 5 pm" -> recipient: "Vijay", message: "Meeting at 5 pm"
                - "WhatsApp Mom: I'll be late" -> recipient: "Mom", message: "I'll be late"
                - "WhatsApp to Jay hello" -> recipient: "Jay", message: "hello"
                - "Send WhatsApp to Sarah good morning" -> recipient: "Sarah", message: "good morning"
                - "Message John hi there" -> recipient: "John", message: "hi there"
                - "text Mom I'm coming home" -> recipient: "Mom", message: "I'm coming home"
                
                Be flexible with:
                - Different word orders
                - Missing punctuation (colons, commas)
                - Natural language patterns
                - Implicit "send" or "message" verbs
                
                Return ONLY in this format:
                RECIPIENT: [name]
                MESSAGE: [message content]
                
                If you cannot parse, return:
                ERROR: Unable to parse command"""
                
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_input)
                ]
                
                response = self.llm.invoke(messages)
                response_text = response.content.strip()
                
                if "ERROR:" in response_text:
                    state['error'] = f"Could not understand the WhatsApp command. Please try formats like: 'WhatsApp to [name] [message]' or 'Send WhatsApp to [name]: [message]'"
                    return state
                
                # Parse the response
                lines = response_text.split('\n')
                recipient = ""
                message = ""
                
                for line in lines:
                    if line.startswith("RECIPIENT:"):
                        recipient = line.replace("RECIPIENT:", "").strip()
                    elif line.startswith("MESSAGE:"):
                        message = line.replace("MESSAGE:", "").strip()
                
                if not recipient or not message:
                    state['error'] = f"Could not extract recipient and message. Please try formats like: 'WhatsApp to [name] [message]' or 'Send WhatsApp to [name]: [message]'"
                    return state
                
                state['parsed_command'] = {
                    "recipient": recipient,
                    "message": message
                }
                
                print(f"[DEBUG] LLM parsing success: {recipient} -> {message}")
                return state
                
            except Exception as e:
                state['error'] = f"Error parsing command: {str(e)}"
                return state
        
        def search_contact_node(state: AgentState) -> AgentState:
            """Search for contact information"""
            if state.get('error'):
                return state
                
            try:
                recipient = state.get('parsed_command', {}).get("recipient", "")
                phone_number = self.contact_tool._run(recipient)
                
                if "not found" in phone_number.lower():
                    state['error'] = f"Contact '{recipient}' not found in your contacts. Please add the contact first."
                    return state
                
                state['contact_info'] = {
                    "name": recipient,
                    "phone": phone_number
                }
                
                return state
                
            except Exception as e:
                state['error'] = f"Error searching contact: {str(e)}"
                return state
        
        def generate_whatsapp_url_node(state: AgentState) -> AgentState:
            """Generate WhatsApp URL"""
            if state.get('error'):
                return state
                
            try:
                phone = state.get('contact_info', {}).get("phone", "")
                message = state.get('parsed_command', {}).get("message", "")
                
                whatsapp_url = self.whatsapp_tool._run(phone, message)
                state['whatsapp_url'] = whatsapp_url
                
                recipient_name = state.get('contact_info', {}).get("name", "")
                state['response_message'] = f"✅ WhatsApp message ready for {recipient_name}! Click the link to send: {whatsapp_url}"
                
                return state
                
            except Exception as e:
                state['error'] = f"Error generating WhatsApp URL: {str(e)}"
                return state
        
        def error_handler_node(state: AgentState) -> AgentState:
            """Handle errors"""
            if state.get('error'):
                state['response_message'] = f"❌ Error: {state['error']}"
            return state
        
        # Build the workflow graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("parse_command", parse_command_node)
        workflow.add_node("search_contact", search_contact_node)
        workflow.add_node("generate_url", generate_whatsapp_url_node)
        workflow.add_node("handle_error", error_handler_node)
        
        # Add edges
        workflow.set_entry_point("parse_command")
        
        def should_continue(state: AgentState) -> str:
            if state.get('error'):
                return "handle_error"
            return "search_contact"
        
        def should_generate_url(state: AgentState) -> str:
            if state.get('error'):
                return "handle_error"
            return "generate_url"
        
        def should_end(state: AgentState) -> str:
            return END
        
        workflow.add_conditional_edges("parse_command", should_continue)
        workflow.add_conditional_edges("search_contact", should_generate_url)
        workflow.add_edge("generate_url", "handle_error")
        workflow.add_edge("handle_error", END)
        
        return workflow.compile()
    
    def process_command(self, user_input: str) -> Dict[str, Any]:
        """Process WhatsApp command using LangGraph workflow"""
        try:
            # Initialize state with proper structure
            initial_state: AgentState = {
                'user_input': user_input,
                'parsed_command': {},
                'contact_info': {},
                'whatsapp_url': '',
                'response_message': '',
                'error': None
            }
            
            # Run the workflow
            result = self.workflow.invoke(initial_state)
            
            return {
                "success": not bool(result.get('error')),
                "message": result.get('response_message', ''),
                "whatsapp_url": result.get('whatsapp_url', ''),
                "error": result.get('error')
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ WhatsApp agent error: {str(e)}",
                "whatsapp_url": "",
                "error": str(e)
            }

# Global agent instance
whatsapp_agent = WhatsAppAgent()