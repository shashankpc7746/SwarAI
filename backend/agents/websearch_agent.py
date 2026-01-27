"""
Web Search Agent for AI Task Automation Assistant
Performs web searches and opens results in browser
"""

import webbrowser
import urllib.parse
import re
from typing import Dict, Any, Optional, TypedDict, ClassVar
from langchain.tools import BaseTool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from config import config

class SearchRequest(BaseModel):
    """Web search request structure"""
    query: str
    engine: str = "google"  # google, bing, duckduckgo, youtube

class AgentState(TypedDict):
    """State for the Web Search agent workflow"""
    user_input: str
    parsed_command: Dict[str, Any]
    search_url: str
    response_message: str
    error: Optional[str]

class WebSearchTool(BaseTool):
    """Tool to perform web searches"""
    name: str = "web_search"
    description: str = "Perform web searches using various search engines"
    
    SEARCH_ENGINES: ClassVar[Dict[str, str]] = {
        "google": "https://www.google.com/search?q=",
        "bing": "https://www.bing.com/search?q=",
        "duckduckgo": "https://duckduckgo.com/?q=",
        "youtube": "https://www.youtube.com/results?search_query=",
        "scholar": "https://scholar.google.com/scholar?q=",
        "maps": "https://www.google.com/maps/search/",
        "images": "https://www.google.com/search?tbm=isch&q=",
    }
    
    def _run(self, query: str, engine: str = "google") -> str:
        """Perform web search"""
        try:
            engine_lower = engine.lower()
            
            # Get search engine URL
            if engine_lower in self.SEARCH_ENGINES:
                base_url = self.SEARCH_ENGINES[engine_lower]
            else:
                base_url = self.SEARCH_ENGINES["google"]
            
            # Build search URL
            encoded_query = urllib.parse.quote(query)
            search_url = base_url + encoded_query
            
            # Open in browser
            webbrowser.open(search_url)
            
            return f"Searching {engine} for: {query}"
            
        except Exception as e:
            return f"Error performing search: {str(e)}"

class WebSearchAgent:
    """LangGraph-powered Web Search Agent"""
    
    def __init__(self):
        # Initialize LLM
        self.llm = ChatGroq(
            groq_api_key=config.GROQ_API_KEY,
            model_name=config.GROQ_MODEL,
            temperature=config.AGENT_TEMPERATURE,
            max_tokens=config.MAX_RESPONSE_TOKENS
        )
        
        # Initialize tools
        self.search_tool = WebSearchTool()
        self.tools = [self.search_tool]
        
        # Build LangGraph workflow
        self.workflow = self._build_workflow()
        
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for web search"""
        
        def parse_command_node(state: AgentState) -> AgentState:
            """Parse user command to extract search query and engine"""
            try:
                user_input = state['user_input']
                
                # Extract search query and engine
                query, engine = self._parse_search_request(user_input)
                
                state['parsed_command'] = {
                    "query": query,
                    "engine": engine
                }
                state['error'] = None
                
            except Exception as e:
                state['error'] = f"Failed to parse search command: {str(e)}"
                state['parsed_command'] = {}
                
            return state
        
        def perform_search_node(state: AgentState) -> AgentState:
            """Perform web search"""
            try:
                if state.get('error'):
                    return state
                
                parsed = state['parsed_command']
                query = parsed.get('query', '')
                engine = parsed.get('engine', 'google')
                
                if not query:
                    state['error'] = "No search query provided"
                    return state
                
                # Perform search
                result = self.search_tool._run(query, engine)
                
                state['search_url'] = f"{engine}:{query}"
                state['response_message'] = f"✅ {result}"
                state['error'] = None
                
            except Exception as e:
                state['error'] = f"Failed to perform search: {str(e)}"
                state['response_message'] = "❌ Search failed"
                
            return state
        
        # Build workflow graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("parse_command", parse_command_node)
        workflow.add_node("perform_search", perform_search_node)
        
        # Add edges
        workflow.set_entry_point("parse_command")
        workflow.add_edge("parse_command", "perform_search")
        workflow.add_edge("perform_search", END)
        
        return workflow.compile()
    
    def _parse_search_request(self, text: str) -> tuple:
        """Parse search request to extract query and engine"""
        text_lower = text.lower()
        
        # Detect search engine
        engine = "google"
        
        if "youtube" in text_lower or "video" in text_lower:
            engine = "youtube"
        elif "bing" in text_lower:
            engine = "bing"
        elif "duckduckgo" in text_lower or "duck" in text_lower:
            engine = "duckduckgo"
        elif "scholar" in text_lower or "research" in text_lower or "paper" in text_lower:
            engine = "scholar"
        elif "maps" in text_lower or "directions" in text_lower or "location" in text_lower:
            engine = "maps"
        elif "image" in text_lower or "picture" in text_lower or "photo" in text_lower:
            engine = "images"
        
        # Extract search query
        query_patterns = [
            r'(?:search|find|look up|google|bing)\s+(?:for\s+)?["\']?([^"\']+)["\']?',
            r'(?:what|who|where|when|why|how)\s+(.+)',
        ]
        
        query = ""
        for pattern in query_patterns:
            match = re.search(pattern, text_lower)
            if match:
                query = match.group(1).strip()
                break
        
        # Fallback: use entire text if no pattern matched
        if not query:
            # Remove common search keywords
            query = text
            for keyword in ["search", "find", "look up", "google", "bing", "for"]:
                query = query.replace(keyword, "")
            query = query.strip()
        
        return (query, engine)
    
    def process_command(self, user_input: str) -> Dict[str, Any]:
        """Process search command and return result"""
        try:
            initial_state = {
                "user_input": user_input,
                "parsed_command": {},
                "search_url": "",
                "response_message": "",
                "error": None
            }
            
            # Run workflow
            final_state = self.workflow.invoke(initial_state)
            
            return {
                "success": final_state.get('error') is None,
                "message": final_state.get('response_message', 'Search processed'),
                "search_url": final_state.get('search_url', ''),
                "details": final_state.get('parsed_command', {})
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Web search error: {str(e)}",
                "search_url": "",
                "details": {}
            }

# Create global instance
websearch_agent = WebSearchAgent()
