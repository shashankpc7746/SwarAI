"""
Calendar Agent for AI Task Automation Assistant
Opens default calendar app with pre-filled event details
"""

import webbrowser
import urllib.parse
import subprocess
import platform
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, TypedDict
from langchain.tools import BaseTool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from config import config

class CalendarEvent(BaseModel):
    """Calendar event structure"""
    title: str
    start_time: str
    end_time: str = ""
    description: str = ""
    location: str = ""

class AgentState(TypedDict):
    """State for the Calendar agent workflow"""
    user_input: str
    parsed_command: Dict[str, Any]
    calendar_url: str
    response_message: str
    error: Optional[str]

class CalendarTool(BaseTool):
    """Tool to create calendar events"""
    name: str = "calendar_creator"
    description: str = "Open default calendar app with pre-filled event details"
    
    def _run(self, title: str, start_time: str, end_time: str = "", description: str = "", location: str = "") -> str:
        """Open calendar with event details"""
        try:
            # Google Calendar URL format
            # Format: https://calendar.google.com/calendar/render?action=TEMPLATE&text=Event&dates=20240101T100000/20240101T110000
            
            # Parse dates
            start_dt = self._parse_datetime(start_time)
            if end_time:
                end_dt = self._parse_datetime(end_time)
            else:
                end_dt = start_dt + timedelta(hours=1)  # Default 1 hour duration
            
            # Format for Google Calendar
            start_formatted = start_dt.strftime("%Y%m%dT%H%M%S")
            end_formatted = end_dt.strftime("%Y%m%dT%H%M%S")
            
            # Build Google Calendar URL
            params = {
                "action": "TEMPLATE",
                "text": title,
                "dates": f"{start_formatted}/{end_formatted}",
                "details": description,
                "location": location
            }
            
            calendar_url = "https://calendar.google.com/calendar/render?" + urllib.parse.urlencode(params)
            
            # Open in browser
            webbrowser.open(calendar_url)
            
            return f"Calendar opened with event: {title} at {start_time}"
            
        except Exception as e:
            return f"Error opening calendar: {str(e)}"
    
    def _parse_datetime(self, time_str: str) -> datetime:
        """Parse various time formats to datetime"""
        try:
            # Try different formats
            formats = [
                "%Y-%m-%d %H:%M",
                "%Y-%m-%d %H:%M:%S",
                "%m/%d/%Y %H:%M",
                "%d/%m/%Y %H:%M",
                "%Y-%m-%dT%H:%M:%S"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(time_str, fmt)
                except:
                    continue
            
            # Fallback: parse relative times like "tomorrow at 3pm"
            return self._parse_relative_time(time_str)
            
        except:
            # Default to current time + 1 hour
            return datetime.now() + timedelta(hours=1)
    
    def _parse_relative_time(self, time_str: str) -> datetime:
        """Parse relative time expressions"""
        now = datetime.now()
        time_str_lower = time_str.lower()
        
        # Tomorrow
        if "tomorrow" in time_str_lower:
            base = now + timedelta(days=1)
        # Today
        elif "today" in time_str_lower:
            base = now
        # Next week
        elif "next week" in time_str_lower:
            base = now + timedelta(weeks=1)
        else:
            base = now
        
        # Extract time (e.g., "3pm", "15:00")
        time_pattern = r'(\d{1,2})\s*(?::(\d{2}))?\s*(am|pm)?'
        match = re.search(time_pattern, time_str_lower)
        
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2)) if match.group(2) else 0
            meridiem = match.group(3)
            
            if meridiem == "pm" and hour < 12:
                hour += 12
            elif meridiem == "am" and hour == 12:
                hour = 0
            
            return base.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        return base

class CalendarAgent:
    """LangGraph-powered Calendar Agent"""
    
    def __init__(self):
        # Initialize LLM
        self.llm = ChatGroq(
            groq_api_key=config.GROQ_API_KEY,
            model_name=config.GROQ_MODEL,
            temperature=config.AGENT_TEMPERATURE,
            max_tokens=config.MAX_RESPONSE_TOKENS
        )
        
        # Initialize tools
        self.calendar_tool = CalendarTool()
        self.tools = [self.calendar_tool]
        
        # Build LangGraph workflow
        self.workflow = self._build_workflow()
        
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for calendar event creation"""
        
        def parse_command_node(state: AgentState) -> AgentState:
            """Parse user command to extract event details"""
            try:
                user_input = state['user_input']
                
                # Use LLM to extract event components
                system_msg = SystemMessage(content="""You are a calendar parsing assistant. Extract the following from the user's command:
                - title: event title/name
                - start_time: when the event starts (format as relative description or specific time)
                - end_time: when the event ends (if mentioned)
                - description: additional details about the event
                - location: where the event takes place
                
                Return ONLY a JSON object with these fields. If not mentioned, use empty string.""")
                
                human_msg = HumanMessage(content=f"Parse this calendar command: {user_input}")
                
                response = self.llm.invoke([system_msg, human_msg])
                
                # Try to parse JSON from response
                import json
                try:
                    parsed = json.loads(response.content)
                except:
                    # Fallback parsing
                    parsed = {
                        "title": self._extract_title(user_input),
                        "start_time": self._extract_time(user_input),
                        "end_time": "",
                        "description": user_input,
                        "location": ""
                    }
                
                state['parsed_command'] = parsed
                state['error'] = None
                
            except Exception as e:
                state['error'] = f"Failed to parse calendar command: {str(e)}"
                state['parsed_command'] = {}
                
            return state
        
        def create_event_node(state: AgentState) -> AgentState:
            """Create calendar event"""
            try:
                if state.get('error'):
                    return state
                
                parsed = state['parsed_command']
                title = parsed.get('title', 'New Event')
                start_time = parsed.get('start_time', 'today')
                end_time = parsed.get('end_time', '')
                description = parsed.get('description', '')
                location = parsed.get('location', '')
                
                # Create event
                result = self.calendar_tool._run(title, start_time, end_time, description, location)
                
                state['calendar_url'] = f"calendar_event_{title}"
                state['response_message'] = f"✅ Calendar event created: {title}"
                state['error'] = None
                
            except Exception as e:
                state['error'] = f"Failed to create calendar event: {str(e)}"
                state['response_message'] = "❌ Failed to create event"
                
            return state
        
        # Build workflow graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("parse_command", parse_command_node)
        workflow.add_node("create_event", create_event_node)
        
        # Add edges
        workflow.set_entry_point("parse_command")
        workflow.add_edge("parse_command", "create_event")
        workflow.add_edge("create_event", END)
        
        return workflow.compile()
    
    def _extract_title(self, text: str) -> str:
        """Extract event title from text"""
        # Look for patterns like "schedule meeting with", "create event for"
        patterns = [
            r'(?:schedule|create|add|set)\s+(?:a\s+)?(?:meeting|event|appointment)\s+(?:for|with|about)\s+([^\.]+)',
            r'(?:meeting|event|appointment)\s+(?:for|about)\s+([^\.]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(1).strip()
        
        # Fallback
        return text[:50]
    
    def _extract_time(self, text: str) -> str:
        """Extract time from text"""
        text_lower = text.lower()
        
        # Look for specific time patterns
        time_patterns = [
            r'(tomorrow|today|next week)\s+at\s+(\d{1,2}\s*(?:am|pm)?)',
            r'on\s+(\w+)\s+at\s+(\d{1,2}\s*(?:am|pm)?)',
            r'at\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)',
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text_lower)
            if match:
                return match.group(0)
        
        # Default to "today"
        return "today"
    
    def process_command(self, user_input: str) -> Dict[str, Any]:
        """Process calendar command and return result"""
        try:
            initial_state = {
                "user_input": user_input,
                "parsed_command": {},
                "calendar_url": "",
                "response_message": "",
                "error": None
            }
            
            # Run workflow
            final_state = self.workflow.invoke(initial_state)
            
            return {
                "success": final_state.get('error') is None,
                "message": final_state.get('response_message', 'Calendar event processed'),
                "calendar_url": final_state.get('calendar_url', ''),
                "details": final_state.get('parsed_command', {})
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Calendar agent error: {str(e)}",
                "calendar_url": "",
                "details": {}
            }

# Create global instance
calendar_agent = CalendarAgent()
