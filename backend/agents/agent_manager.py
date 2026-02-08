"""
Multi-Agent Coordinator (MCP) for AI Task Automation Assistant
Handles routing commands to appropriate agents using LangGraph
"""

from typing import Dict, Any, List, Optional, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from agents.whatsapp_agent import whatsapp_agent
from agents.conversation_agent import conversation_agent
from agents.filesearch_agent import filesearch_agent
from agents.email_agent import email_agent
from agents.calendar_agent import calendar_agent
from agents.phone_agent import phone_agent
from agents.payment_agent import payment_agent
from agents.app_launcher_agent import app_launcher_agent
from agents.websearch_agent import websearch_agent
from agents.task_agent import task_agent
from agents.screenshot_agent import screenshot_agent
from agents.system_control_agent import system_control_agent
from config import config
from utils.conversation_memory import conversation_memory
from utils.conversational_tts import conversational_tts
from utils.feature_request_logger import feature_logger
from agents.multi_task_orchestrator import MultiTaskOrchestrator

class AgentManagerState(TypedDict):
    """State for the agent manager workflow"""
    user_input: str
    original_input: str  # Store original before enhancement
    enhanced_input: str  # AI-enhanced version
    detected_intent: str
    agent_name: str
    agent_response: Dict[str, Any]
    final_response: str
    error: Optional[str]

class AgentManager:
    """
    Multi-Agent Coordinator (MCP) that routes commands to appropriate agents
    Uses LangGraph for stateful workflow management
    """
    
    def __init__(self):
        # Initialize LLM for intent detection
        self.llm = ChatGroq(
            groq_api_key=config.GROQ_API_KEY,
            model_name=config.GROQ_MODEL,
            temperature=config.AGENT_TEMPERATURE,
            max_tokens=config.MAX_RESPONSE_TOKENS
        )
        
        # Register available agents
        self.agents = {
            "whatsapp": whatsapp_agent,
            "conversation": conversation_agent,
            "filesearch": filesearch_agent,
            "email": email_agent,
            "calendar": calendar_agent,
            "phone": phone_agent,
            "payment": payment_agent,
            "app_launcher": app_launcher_agent,
            "websearch": websearch_agent,
            "task": task_agent,
            "screenshot": screenshot_agent,
            "system_control": system_control_agent
        }
        
        # Initialize multi-task orchestrator
        self.orchestrator = MultiTaskOrchestrator(self)
        
        # Build MCP workflow
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the MCP workflow for agent coordination"""
        
        def ai_enhancement_node(state: AgentManagerState) -> AgentManagerState:
            """
            UNIVERSAL AI ENHANCEMENT LAYER
            Process ALL commands through Groq AI to understand natural language better
            Converts casual/messy speech into clear, structured commands
            """
            try:
                original_input = state['user_input']
                
                # Store original
                state['original_input'] = original_input
                
                print(f"\n[DEBUG] AI Enhancement Layer:")
                print(f"[DEBUG] Original: '{original_input}'")
                
                # Use Groq AI to enhance and clarify the command
                system_msg = SystemMessage(content="""You are an intelligent command enhancement AI. 
Your job is to understand what the user REALLY wants to do, even if they speak casually or make typos.

ENHANCEMENT RULES:
1. Fix typos and spacing - but PRESERVE word order as spoken
2. For email addresses with "at the rate", convert to @ symbol and keep name-number order:
   - "shashank gupta 7746 at the rate gmail.com" → "shashankgupta7746@gmail.com" (lowercase, no spaces)
   - "john 123 at rate test.com" → "john123@test.com"
   - NEVER reorder: "shashank 7746" stays "shashank7746", NOT "7746shashank"
3. Clarify vague requests (e.g., "find that apple thing" → "find apple.pdf file")
4. Expand abbreviated commands (e.g., "msg Jay" → "send WhatsApp message to Jay")
5. Preserve all important details (names, numbers, subjects, context)
6. Make commands more specific and actionable
7. Keep the intent clear (email, call, search, etc.)
8. Add missing context when obvious (e.g., "send to Jay" → identify what to send)
9. For system control commands (volume, brightness, battery, time), preserve them EXACTLY as spoken - DO NOT change or add words
10. For information questions about people or topics (who is, tell me about), DO NOT convert to file search - keep as information query

EXAMPLES:
Input: "send mail to Shashank Gupta 7746 at the rate gmail.com wishing happy birthday"
Output: "send email to shashankgupta7746@gmail.com with subject 'Happy Birthday' and write a birthday wish"

Input: "send email to Jay his email is john 123 at rate example.com subject internship"
Output: "send email to john123@example.com with subject 'internship application'"

Input: "call jay"
Output: "call Jay"

Input: "find that ownership doc"
Output: "find ownership document file"

Input: "msg mom about dinner"
Output: "send WhatsApp message to Mom saying let's have dinner"

Input: "pay 100 to jay paytm"
Output: "send payment of Rs 100 to Jay using Paytm"

Input: "open apple pdf from file"
Output: "open apple.pdf file"

Input: "search for cats on youtube"
Output: "search for cats on YouTube"

Input: "increase volume"
Output: "increase volume"

Input: "volume up"
Output: "volume up"

Input: "make it louder"
Output: "increase volume"

Input: "check battery"
Output: "battery status"

Input: "who is Jay"
Output: "who is Jay"

Input: "tell me about Shashank"
Output: "tell me about Shashank"

Input: "what do you know about John"
Output: "what do you know about John"

Input: "send my recent whatsapp chat to"
Output: "send WhatsApp message about recent conversation to"

Input: "share the conversation we had"
Output: "send WhatsApp message about our conversation"

IMPORTANT:
- Return ONLY the enhanced command, no explanations
- Keep it natural and conversational
- Don't over-complicate simple commands
- Preserve the user's intent exactly
- System control commands should remain simple and clear
- Information queries should stay as questions, not file searches""")                
                human_msg = HumanMessage(content=f"Enhance this command: {original_input}")
                
                try:
                    response = self.llm.invoke([system_msg, human_msg])
                    enhanced_input = response.content.strip()
                    
                    # Basic validation - if AI returns something weird, use original
                    if len(enhanced_input) > len(original_input) * 3 or len(enhanced_input) < 3:
                        print(f"[DEBUG] AI enhancement seems off, using original")
                        enhanced_input = original_input
                    
                    state['enhanced_input'] = enhanced_input
                    state['user_input'] = enhanced_input  # Use enhanced version for routing
                    
                    print(f"[DEBUG] Enhanced: '{enhanced_input}'")
                    
                    if original_input != enhanced_input:
                        print(f"[DEBUG] ✨ Command was enhanced by AI")
                    else:
                        print(f"[DEBUG] Command unchanged")
                        
                except Exception as e:
                    print(f"[DEBUG] AI enhancement failed: {str(e)}, using original")
                    state['enhanced_input'] = original_input
                    state['user_input'] = original_input
                
            except Exception as e:
                print(f"[DEBUG] Enhancement error: {str(e)}")
                state['enhanced_input'] = state['user_input']
                state['original_input'] = state['user_input']
            
            return state
        
        def intent_detection_node(state: AgentManagerState) -> AgentManagerState:
            """Enhanced intent detection with conversational AI and natural language understanding"""
            try:
                # Initialize default values if not present
                if 'detected_intent' not in state:
                    state['detected_intent'] = ""
                if 'agent_name' not in state:
                    state['agent_name'] = ""
                if 'error' not in state:
                    state['error'] = None
                
                user_input = state['user_input']
                
                # Check for multi-task workflows FIRST (highest priority)
                if self.orchestrator.detect_multi_task(user_input):
                    state['detected_intent'] = "multi_task"
                    state['agent_name'] = "multi_task"
                    print(f"[DEBUG] Multi-task workflow detected")
                    return state
                user_input_lower = user_input.lower()
                
                print(f"\n[DEBUG] Intent Detection:")
                print(f"[DEBUG] User input: '{user_input}'")
                
                # Check conversational input first
                is_conversational = conversation_agent.is_conversational_input(user_input)
                print(f"[DEBUG] Is conversational: {is_conversational}")
                
                # Enhanced keyword detection with NLP patterns
                file_keywords = ["find", "search", "open", "file", "document", "folder", "pdf", "doc", "excel", "photo", "video", "music", "ownership", "report", "presentation"]
                whatsapp_keywords = ["whatsapp", "message", "send to", "text", "tell", "let know", "inform", "send whatsapp", "whatsapp to", "message to", "share"]
                email_keywords = ["email", "send email", "compose email", "draft email", "mail to"]
                calendar_keywords = ["calendar", "schedule", "schedule meeting", "create event", "add event", "appointment", "set reminder at", "remind me at"]
                phone_keywords = ["call", "phone", "dial", "ring", "make a call"]
                payment_keywords = ["pay", "payment", "send money", "transfer", "paypal", "googlepay", "paytm", "phonepe"]
                app_keywords = ["open", "launch", "start", "run", "chrome", "browser", "notepad", "calculator"]
                search_keywords = ["google", "search for", "look up", "find on google", "youtube", "browse"]
                task_keywords = ["task", "todo", "remind me", "reminder", "add task", "create task", "list tasks"]
                screenshot_keywords = ["screenshot", "capture screen", "screen capture", "take screenshot", "capture", "take a screenshot"]
                system_control_keywords = ["volume", "mute", "unmute", "lock", "shutdown", "restart", "reboot", "sleep", "hibernate", "louder", "quieter", "volume up", "volume down", "increase volume", "decrease volume", "lock screen", "shut down", "turn off", "brightness", "brightness up", "brightness down", "brighter", "dimmer", "battery", "battery status", "battery level", "time", "what time", "current time", "what's the time"]
                
                # Detect file intent with better distinction
                file_keywords = ["find", "search", "open", "ownership", "folder", "photo", "video", "pdf", "doc", "docx", "excel", "presentation", "report"]
                
                # Information queries about people or topics (should go to conversation)
                information_questions = ["who is", "who's", "tell me about", "what do you know about", "information about", "details about", "tell me more about", "what is", "what's", "explain", "describe"]
                capability_questions = ["can you", "are you able", "do you", "what can", "how do", "why", "how"]
                general_questions = ["what", "how", "why", "when", "where", "who", "?"]
                
                # Check if it's an information query about a person/topic
                is_information_query = any(phrase in user_input_lower for phrase in information_questions)
                is_capability_question = any(phrase in user_input_lower for phrase in capability_questions)
                is_general_question = any(word in user_input_lower for word in general_questions) and not any(op_word in user_input_lower for op_word in ["find", "search", "open", "send"])
                
                # Actual file operations (should go to filesearch)
                # Must have file-related context AND operation keywords
                file_extensions = [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".txt", ".jpg", ".png", ".mp4", ".mp3"]
                file_context = ["file", "document", "folder", "pdf", "doc", "excel", "photo", "video", "music", "ownership", "report", "presentation"]
                file_operation_keywords = ["find", "search", "open", "locate", "show me"]
                
                has_file_context = any(ctx in user_input_lower for ctx in file_context) or any(ext in user_input_lower for ext in file_extensions)
                has_file_operation = any(keyword in user_input_lower for keyword in file_operation_keywords) and has_file_context and not is_information_query and not is_capability_question
                
                # Multi-agent detection (file + communication)
                has_whatsapp_intent = any(keyword in user_input_lower for keyword in whatsapp_keywords)
                has_email_intent = any(keyword in user_input_lower for keyword in email_keywords)
                has_calendar_intent = any(keyword in user_input_lower for keyword in calendar_keywords)
                has_phone_intent = any(keyword in user_input_lower for keyword in phone_keywords)
                has_payment_intent = any(keyword in user_input_lower for keyword in payment_keywords)
                has_app_intent = any(keyword in user_input_lower for keyword in app_keywords)
                has_search_intent = any(keyword in user_input_lower for keyword in search_keywords)
                has_task_intent = any(keyword in user_input_lower for keyword in task_keywords)
                has_screenshot_intent = any(keyword in user_input_lower for keyword in screenshot_keywords)
                has_system_control_intent = any(keyword in user_input_lower for keyword in system_control_keywords)
                
                # Special handling for multi-agent patterns
                multi_agent_patterns = ["send * to", "share * with", "find * and send", "send the * file"]
                is_multi_agent_command = any("send" in user_input_lower and keyword in user_input_lower for keyword in file_keywords)
                
                # Special handling for WhatsApp patterns
                whatsapp_patterns = ["send whatsapp", "whatsapp to", "message to", "text to"]
                is_whatsapp_command = any(pattern in user_input_lower for pattern in whatsapp_patterns)
                
                print(f"[DEBUG] Is information query: {is_information_query}")
                print(f"[DEBUG] Is capability question: {is_capability_question}")
                print(f"[DEBUG] Is general question: {is_general_question}")
                print(f"[DEBUG] Has file context: {has_file_context}")
                print(f"[DEBUG] Has file operation: {has_file_operation}")
                print(f"[DEBUG] Has WhatsApp intent: {has_whatsapp_intent}")
                print(f"[DEBUG] Has Email intent: {has_email_intent}")
                print(f"[DEBUG] Has Calendar intent: {has_calendar_intent}")
                print(f"[DEBUG] Has Phone intent: {has_phone_intent}")
                print(f"[DEBUG] Has Payment intent: {has_payment_intent}")
                print(f"[DEBUG] Has App intent: {has_app_intent}")
                print(f"[DEBUG] Has Search intent: {has_search_intent}")
                print(f"[DEBUG] Has Task intent: {has_task_intent}")
                print(f"[DEBUG] Has Screenshot intent: {has_screenshot_intent}")
                print(f"[DEBUG] Has System Control intent: {has_system_control_intent}")
                print(f"[DEBUG] Is WhatsApp command: {is_whatsapp_command}")
                print(f"[DEBUG] Is multi-agent command: {is_multi_agent_command}")
                
                # Priority routing: Check for specific agent intents first
                
                # Information queries about people/topics (HIGH PRIORITY - before file search)
                if is_information_query and not has_file_context:
                    state['detected_intent'] = "conversation"
                    state['agent_name'] = "conversation"
                    print(f"[DEBUG] Routed to: conversation (information query)")
                    return state
                
                # System control commands (high priority - specific actions)
                if has_system_control_intent:
                    state['detected_intent'] = "system_control"
                    state['agent_name'] = "system_control"
                    print(f"[DEBUG] Routed to: system_control")
                    return state
                
                # Screenshot commands
                elif has_screenshot_intent:
                    state['detected_intent'] = "screenshot"
                    state['agent_name'] = "screenshot"
                    print(f"[DEBUG] Routed to: screenshot")
                    return state
                
                # Payment commands
                elif has_payment_intent:
                    state['detected_intent'] = "payment"
                    state['agent_name'] = "payment"
                    print(f"[DEBUG] Routed to: payment")
                    return state
                
                # Phone/Call commands
                elif has_phone_intent:
                    state['detected_intent'] = "phone"
                    state['agent_name'] = "phone"
                    print(f"[DEBUG] Routed to: phone")
                    return state
                
                # WhatsApp commands (MOVED UP - higher priority than calendar)
                # This prevents "message" keyword from triggering calendar
                elif is_whatsapp_command or (has_whatsapp_intent and not has_file_operation and not is_capability_question):
                    state['detected_intent'] = "whatsapp"
                    state['agent_name'] = "whatsapp"
                    print(f"[DEBUG] Routed to: whatsapp")
                    return state
                
                # Multi-agent commands (file + communication)
                elif is_multi_agent_command or (has_file_operation and has_whatsapp_intent):
                    state['detected_intent'] = "multi_agent"
                    state['agent_name'] = "multi_agent"
                    print(f"[DEBUG] Routed to: multi_agent (file + whatsapp)")
                    return state
                
                # Calendar commands (moved down to avoid conflicts with WhatsApp)
                elif has_calendar_intent and not has_whatsapp_intent:
                    state['detected_intent'] = "calendar"
                    state['agent_name'] = "calendar"
                    print(f"[DEBUG] Routed to: calendar")
                    return state
                
                # Email commands
                elif has_email_intent and not has_whatsapp_intent:
                    state['detected_intent'] = "email"
                    state['agent_name'] = "email"
                    print(f"[DEBUG] Routed to: email")
                    return state
                
                # Task management commands
                elif has_task_intent:
                    state['detected_intent'] = "task"
                    state['agent_name'] = "task"
                    print(f"[DEBUG] Routed to: task")
                    return state
                
                # Web search commands
                elif has_search_intent and not has_file_operation:
                    state['detected_intent'] = "websearch"
                    state['agent_name'] = "websearch"
                    print(f"[DEBUG] Routed to: websearch")
                    return state
                
                # App launcher commands (open/launch apps)
                elif has_app_intent and not has_file_operation:
                    state['detected_intent'] = "app_launcher"
                    state['agent_name'] = "app_launcher"
                    print(f"[DEBUG] Routed to: app_launcher")
                    return state
                
                # File operations (actual operations, not capability questions)
                elif has_file_operation and not is_capability_question and not is_general_question:
                    state['detected_intent'] = "filesearch"
                    state['agent_name'] = "filesearch"
                    print(f"[DEBUG] Routed to: filesearch")
                    return state
                
                # Capability questions and general questions go to conversation
                elif is_capability_question or is_general_question:
                    state['detected_intent'] = "conversation"
                    state['agent_name'] = "conversation"
                    print(f"[DEBUG] Routed to: conversation (capability/general question)")
                    return state
                
                # Pure conversational input
                elif is_conversational:
                    state['detected_intent'] = "conversation"
                    state['agent_name'] = "conversation"
                    print(f"[DEBUG] Routed to: conversation (pure conversational)")
                    return state
                
                # Use LLM for complex intent detection
                print(f"[DEBUG] Using LLM for intent detection...")
                
                system_prompt = """You are SwarAI, an advanced AI assistant with natural language understanding.
                Analyze the user input and classify it into the most appropriate category:
                
                AVAILABLE AGENTS:
                - whatsapp: WhatsApp messaging and communication
                  * Patterns: "send message", "whatsapp", "text someone", "message [name]"
                  * Natural: "tell mom I'm coming", "let dad know about meeting", "send hello to friend"
                
                - email: Email composition and sending
                  * Patterns: "send email", "email to", "compose email", "mail"
                  * Natural: "email boss about meeting", "send email to john"
                
                - calendar: Schedule meetings and events
                  * Patterns: "schedule", "meeting", "calendar", "appointment", "event"
                  * Natural: "schedule meeting tomorrow", "create event for Monday"
                
                - phone: Make phone calls
                  * Patterns: "call", "phone", "dial", "ring"
                  * Natural: "call mom", "phone vijay", "make a call to boss"
                
                - payment: Send payments via various apps
                  * Patterns: "pay", "send money", "payment", "paypal", "googlepay"
                  * Natural: "pay $50 to john", "send 100 rupees via paytm"
                
                - app_launcher: Open applications and programs
                  * Patterns: "open", "launch", "start", "run"
                  * Natural: "open chrome", "launch calculator", "start notepad"
                
                - websearch: Web searches and browsing
                  * Patterns: "google", "search", "look up", "find on google"
                  * Natural: "google python tutorials", "search for restaurants"
                
                - task: Task and reminder management
                  * Patterns: "add task", "remind me", "todo", "task list"
                  * Natural: "remind me to call mom", "add task buy groceries"
                  
                - filesearch: File operations, search, open, and sharing
                  * Patterns: "find file", "open document", "search for", "locate", "show me files"
                  * Natural: "where is my report", "open that presentation", "find my photos"
                  
                - conversation: Conversational interactions, greetings, help
                  * Patterns: "hello", "help", "what can you do", "who are you", "thanks"
                  * Natural: "hi there", "I need help", "goodbye", "thank you"
                  
                - multi_agent: Complex tasks requiring multiple agents (FILE + COMMUNICATION)
                  * Patterns: "send [file] to [contact]", "find and share", "search and message"
                  * Natural: "send my report to boss on whatsapp", "find photo and share with mom"
                  * Key indicators: file words + communication words together
                
                CLASSIFICATION RULES:
                1. If command contains BOTH file operations AND communication -> multi_agent
                2. If contains file words (document, file, report, ownership, photo, etc.) AND send/share/message words -> multi_agent
                3. If clear WhatsApp/messaging intent only -> whatsapp  
                4. If clear file operation intent only -> filesearch
                5. If conversational/greeting -> conversation
                6. If unclear -> conversation (SwarAI will ask for clarification)
                
                Examples:
                - "Send report.pdf to boss on WhatsApp" -> multi_agent
                - "Send the ownership file to jay" -> multi_agent (file + send)
                - "Find ownership document and send to jay" -> multi_agent
                - "Share my presentation with team" -> multi_agent
                - "Tell Sarah I'm running late" -> whatsapp
                - "Find my Excel files" -> filesearch
                - "Open presentation.pptx" -> filesearch
                - "Send hello to mom" -> whatsapp
                - "Hi, what can you do?" -> conversation
                - "Where are my documents?" -> filesearch
                
                Return ONLY the agent name. Nothing else."""
                
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_input)
                ]
                
                response = self.llm.invoke(messages)
                intent = response.content.strip().lower()
                
                print(f"[DEBUG] LLM detected intent: '{intent}'")
                
                # Enhanced intent validation with fallbacks
                if intent in self.agents or intent == "multi_agent":
                    state['detected_intent'] = intent
                    state['agent_name'] = intent
                    print(f"[DEBUG] Final routing: {intent}")
                else:
                    # Default to conversation for unknown intents
                    state['detected_intent'] = "conversation"
                    state['agent_name'] = "conversation"
                    print(f"[DEBUG] Unknown intent '{intent}', defaulting to conversation")
                
                return state
                
            except Exception as e:
                print(f"[DEBUG] Error in intent detection: {str(e)}")
                state['error'] = f"Error in intent detection: {str(e)}"
                return state
        
        def route_to_agent_node(state: AgentManagerState) -> AgentManagerState:
            """Enhanced routing with multi-agent coordination"""
            if state.get('error'):
                return state
            
            try:
                agent_name = state.get('agent_name')
                user_input = state['user_input']
                
                # Handle multi-task workflows
                if agent_name == "multi_task":
                    state['agent_response'] = self.orchestrator.execute_workflow(user_input)
                    return state
                
                # Handle old multi-agent workflows (deprecated, use multi_task instead)
                elif agent_name == "multi_agent":
                    state['agent_response'] = self._handle_multi_agent_workflow(user_input)
                    return state
                
                # Route to specific agents
                if agent_name == "conversation":
                    state['agent_response'] = self.agents["conversation"].process_conversation(user_input)
                elif agent_name == "whatsapp":
                    state['agent_response'] = self.agents["whatsapp"].process_command(user_input)
                elif agent_name == "filesearch":
                    state['agent_response'] = self.agents["filesearch"].process_command(user_input)
                elif agent_name == "email":
                    state['agent_response'] = self.agents["email"].process_command(user_input)
                elif agent_name == "calendar":
                    state['agent_response'] = self.agents["calendar"].process_command(user_input)
                elif agent_name == "phone":
                    state['agent_response'] = self.agents["phone"].process_command(user_input)
                elif agent_name == "payment":
                    state['agent_response'] = self.agents["payment"].process_command(user_input)
                elif agent_name == "app_launcher":
                    state['agent_response'] = self.agents["app_launcher"].process_command(user_input)
                elif agent_name == "websearch":
                    state['agent_response'] = self.agents["websearch"].process_command(user_input)
                elif agent_name == "task":
                    state['agent_response'] = self.agents["task"].process_command(user_input)
                elif agent_name == "screenshot":
                    state['agent_response'] = self.agents["screenshot"].process_command(user_input)
                elif agent_name == "system_control":
                    state['agent_response'] = self.agents["system_control"].process_command(user_input)
                else:
                    # Log unimplemented feature request
                    feature_logger.log_request(
                        user_input=user_input,
                        detected_intent=state.get('detected_intent', 'unknown'),
                        reason="No matching agent found",
                        context={
                            "original_input": state.get('original_input'),
                            "enhanced_input": state.get('enhanced_input')
                        }
                    )
                    
                    # Fallback with feature request message
                    state['agent_response'] = {
                        "success": False,
                        "message": feature_logger.get_user_message(user_input),
                        "intent": "unimplemented",
                        "context": {"feature_logged": True}
                    }
                
                return state
                
            except Exception as e:
                state['error'] = f"Error routing to agent: {str(e)}"
                state['agent_response'] = {
                    "success": False,
                    "message": f"Hi! I'm SwarAI. I encountered a small issue: {str(e)}. Please try again!",
                    "error": str(e)
                }
                return state
        
        def generate_response_node(state: AgentManagerState) -> AgentManagerState:
            """Generate final response based on agent output"""
            try:
                if state.get('error'):
                    state['final_response'] = f"❌ System Error: {state['error']}"
                    return state
                
                agent_response = state.get('agent_response', {})
                
                if agent_response.get("success", False):
                    state['final_response'] = agent_response.get("message", "✅ Task completed successfully!")
                else:
                    error_msg = agent_response.get("error", "Unknown error occurred")
                    state['final_response'] = agent_response.get("message", f"❌ Error: {error_msg}")
                
                return state
                
            except Exception as e:
                state['final_response'] = f"❌ Error generating response: {str(e)}"
                return state
        
        # Build the workflow graph
        workflow = StateGraph(AgentManagerState)
        
        # Add nodes (AI Enhancement is now the FIRST step)
        workflow.add_node("ai_enhance", ai_enhancement_node)  # NEW: Universal AI enhancement
        workflow.add_node("detect_intent", intent_detection_node)
        workflow.add_node("route_to_agent", route_to_agent_node)
        workflow.add_node("generate_response", generate_response_node)
        
        # Add edges (AI Enhancement → Intent Detection → Route → Response)
        workflow.set_entry_point("ai_enhance")  # Start with AI enhancement
        workflow.add_edge("ai_enhance", "detect_intent")  # Then detect intent
        workflow.add_edge("detect_intent", "route_to_agent")
        workflow.add_edge("route_to_agent", "generate_response")
        workflow.add_edge("generate_response", END)
        
        return workflow.compile()
    
    def _handle_multi_agent_workflow(self, user_input: str) -> Dict[str, Any]:
        """Handle complex workflows requiring multiple agents"""
        try:
            # For simple WhatsApp messages without file operations, route directly to WhatsApp agent
            user_input_lower = user_input.lower()
            file_terms = ["ownership", "document", "file", "report", "presentation", "photo", "video", "pdf", "doc"]
            has_file_intent = any(term in user_input_lower for term in file_terms)
            
            print(f"[DEBUG] Multi-agent workflow called for: {user_input}")
            print(f"[DEBUG] Has file intent: {has_file_intent}")
            
            # If it's just a WhatsApp message without file operations, delegate to WhatsApp agent
            if not has_file_intent and any(pattern in user_input_lower for pattern in ["send whatsapp", "whatsapp to", "message to"]):
                print(f"[DEBUG] Multi-agent delegating to WhatsApp agent: {user_input}")
                whatsapp_result = self.agents["whatsapp"].process_command(user_input)
                return whatsapp_result
            
            # First, try to parse the multi-agent intent
            system_prompt = """Analyze this command to determine the multi-agent workflow needed:
            
            WORKFLOW TYPES:
            1. file_to_whatsapp: Find/prepare file and send via WhatsApp
            2. search_and_share: Search for files and prepare for sharing
            3. open_and_inform: Open file and notify someone
            4. whatsapp_only: Simple WhatsApp message without files
            
            Extract:
            - workflow_type: [file_to_whatsapp/search_and_share/open_and_inform/whatsapp_only]
            - file_query: [file name/pattern to find] (empty if no file)
            - recipient: [person to send to] (NEVER extract 'to', 'for', or prepositions)
            - message: [optional message content]
            
            IMPORTANT: For recipient extraction, identify the actual person's name:
            - "send WhatsApp message to Jay lion is coming" -> recipient: "Jay", message: "lion is coming"
            - "send report.pdf to boss" -> recipient: "boss", file: "report.pdf"
            - "message mom about dinner" -> recipient: "mom", message: "about dinner"
            
            NEVER extract prepositions (to, for, with, about) as recipient names.
            
            Examples:
            - "Send report.pdf to boss on WhatsApp" -> file_to_whatsapp, report.pdf, boss
            - "Find my photos and share with mom" -> search_and_share, photos, mom
            - "Send WhatsApp message to Jay lion is coming" -> whatsapp_only, (empty), Jay, lion is coming
            
            Return format:
            WORKFLOW: [type]
            FILE: [query]
            RECIPIENT: [name]
            MESSAGE: [content or empty]
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_input)
            ]
            
            response = self.llm.invoke(messages)
            response_text = response.content.strip()
            
            print(f"[DEBUG] LLM parsing response: {response_text}")
            
            # Parse workflow parameters
            workflow_type = ""
            file_query = ""
            recipient = ""
            message = ""
            
            for line in response_text.split('\n'):
                if line.startswith("WORKFLOW:"):
                    workflow_type = line.replace("WORKFLOW:", "").strip()
                elif line.startswith("FILE:"):
                    file_query = line.replace("FILE:", "").strip()
                elif line.startswith("RECIPIENT:"):
                    recipient = line.replace("RECIPIENT:", "").strip()
                    # Additional validation to prevent extracting prepositions
                    if recipient.lower() in ["to", "for", "with", "about", "from", "the", "a", "an"]:
                        print(f"[DEBUG] Ignoring invalid recipient: {recipient}")
                        recipient = ""
                elif line.startswith("MESSAGE:"):
                    message = line.replace("MESSAGE:", "").strip()
            
            print(f"[DEBUG] Parsed - Workflow: {workflow_type}, File: {file_query}, Recipient: {recipient}, Message: {message}")
            
            # Execute the multi-agent workflow
            if workflow_type == "file_to_whatsapp" and file_query and recipient:
                return self._execute_file_to_whatsapp_workflow(file_query, recipient, message)
            elif workflow_type == "search_and_share" and file_query:
                return self._execute_search_and_share_workflow(file_query, recipient)
            elif workflow_type == "whatsapp_only" and recipient:
                # For simple WhatsApp messages, delegate to WhatsApp agent
                whatsapp_command = f"Send WhatsApp to {recipient}: {message}" if message else f"Send WhatsApp to {recipient}"
                print(f"[DEBUG] Multi-agent creating WhatsApp command: {whatsapp_command}")
                whatsapp_result = self.agents["whatsapp"].process_command(whatsapp_command)
                return whatsapp_result
            else:
                # Fallback to generic workflow
                return self._execute_generic_multi_agent_workflow(user_input)
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Hi! I'm SwarAI. I had trouble understanding that multi-agent request. Error: {str(e)}",
                "workflow": "multi_agent_error",
                "error": str(e)
            }
    
    def _execute_generic_multi_agent_workflow(self, user_input: str) -> Dict[str, Any]:
        """Execute generic multi-agent workflow when pattern isn't clear"""
        try:
            # Use LLM to understand what the user wants and execute it
            system_prompt = """You are SwarAI, an AI assistant that executes tasks directly.
            
            The user gave a command that involves multiple actions. Analyze it and execute the appropriate workflow:
            
            AVAILABLE ACTIONS:
            1. Find/search files: Use filesearch agent
            2. Send WhatsApp messages: Use whatsapp agent 
            3. Combined file + messaging: Execute both in sequence
            
            EXECUTION APPROACH:
            - Don't ask for clarification - execute what makes the most sense
            - If file mentioned, try to find it first
            - If messaging mentioned, create WhatsApp message
            - If both, do file search then messaging
            
            Parse this command and determine the best execution path:
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_input)
            ]
            
            response = self.llm.invoke(messages)
            analysis = response.content.strip()
            
            # Try to extract file and recipient info from the original command
            user_input_lower = user_input.lower()
            
            # Extract potential file references
            file_terms = ["ownership", "document", "file", "report", "presentation", "photo", "video", "pdf", "doc"]
            mentioned_files = [term for term in file_terms if term in user_input_lower]
            
            # Extract potential recipients (improved logic to avoid extracting prepositions)
            words = user_input.split()
            potential_recipients = []
            for i, word in enumerate(words):
                if word.lower() in ["to", "for"] and i + 1 < len(words):
                    next_word = words[i + 1]
                    # Skip common words that aren't names
                    if next_word.lower() not in ["the", "a", "an", "my", "your", "his", "her", "their", "our", "whatsapp", "message", "file"]:
                        potential_recipients.append(next_word)
            
            print(f"[DEBUG] Generic multi-agent - Files: {mentioned_files}, Recipients: {potential_recipients}")
            
            # If we found file references and recipients, execute file-to-whatsapp workflow
            if mentioned_files and potential_recipients:
                file_query = mentioned_files[0]
                recipient = potential_recipients[0]
                return self._execute_file_to_whatsapp_workflow(file_query, recipient)
            
            # If only file mentioned, do file search
            elif mentioned_files:
                file_result = self.agents["filesearch"].process_command(f"find {mentioned_files[0]}")
                if file_result.get("success"):
                    return {
                        "success": True,
                        "message": f"✅ Found files related to '{mentioned_files[0]}'! {file_result.get('message', '')}",
                        "workflow": "file_search",
                        "file_results": file_result.get("search_results", [])
                    }
                else:
                    return {
                        "success": False,
                        "message": f"🔍 I couldn't find any files related to '{mentioned_files[0]}'. Could you be more specific?",
                        "workflow": "file_search_failed"
                    }
            
            # If messaging intent detected, handle as WhatsApp
            elif any(word in user_input_lower for word in ["send", "message", "tell", "whatsapp"]):
                print(f"[DEBUG] Generic multi-agent delegating to WhatsApp: {user_input}")
                whatsapp_result = self.agents["whatsapp"].process_command(user_input)
                return whatsapp_result
            
            # Fallback - execute direct action instead of giving guidance
            else:
                # Instead of generic guidance, try to execute the most likely action
                return self.agents["conversation"].process_conversation(user_input)
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Hi! I'm SwarAI. I had trouble with that request. Could you try rephrasing it? Error: {str(e)}",
                "workflow": "generic_error",
                "error": str(e)
            }
    
    def _execute_file_to_whatsapp_workflow(self, file_query: str, recipient: str, custom_message: str = "") -> Dict[str, Any]:
        """Execute file search + WhatsApp sharing workflow"""
        try:
            # Step 1: Search for the file
            file_result = self.agents["filesearch"].process_command(f"find {file_query}")
            
            if not file_result.get("success") or not file_result.get("search_results"):
                return {
                    "success": False,
                    "message": f"🔍 I couldn't find '{file_query}'. Please check the filename and try again.",
                    "workflow": "file_to_whatsapp",
                    "step": "file_search_failed"
                }
            
            # Get the best matching file
            best_file = file_result["search_results"][0]["file_info"]
            file_name = best_file["name"]
            file_path = best_file["path"]
            file_size_mb = best_file["size"] / (1024 * 1024)
            
            # Step 2: Prepare sharing message
            if custom_message:
                sharing_text = custom_message
            else:
                sharing_text = f"📁 Sharing file: {file_name} ({file_size_mb:.1f}MB)"
            
            # Step 3: Create WhatsApp message
            whatsapp_command = f"Send WhatsApp to {recipient}: {sharing_text}"
            whatsapp_result = self.agents["whatsapp"].process_command(whatsapp_command)
            
            if whatsapp_result.get("success"):
                return {
                    "success": True,
                    "message": f"✅ Great! I found '{file_name}' and prepared WhatsApp message for {recipient}!\n\n📁 File: {file_name} ({file_size_mb:.1f}MB)\n💬 {whatsapp_result['message']}",
                    "workflow": "file_to_whatsapp",
                    "file_info": best_file,
                    "whatsapp_result": whatsapp_result,
                    "whatsapp_url": whatsapp_result.get("whatsapp_url", "")
                }
            else:
                return {
                    "success": False,
                    "message": f"📁 I found '{file_name}' but couldn't create WhatsApp message: {whatsapp_result.get('message', 'Unknown error')}",
                    "workflow": "file_to_whatsapp",
                    "step": "whatsapp_failed"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Hi! I'm SwarAI. I had trouble with that file sharing request. Error: {str(e)}",
                "workflow": "file_to_whatsapp",
                "error": str(e)
            }
    
    def _execute_search_and_share_workflow(self, file_query: str, recipient: str = "") -> Dict[str, Any]:
        """Execute file search and prepare for sharing"""
        try:
            # Search for files
            file_result = self.agents["filesearch"].process_command(f"search {file_query}")
            
            if not file_result.get("success") or not file_result.get("search_results"):
                return {
                    "success": False,
                    "message": f"🔍 No files found matching '{file_query}'. Try a different search term.",
                    "workflow": "search_and_share"
                }
            
            # Format results for sharing
            results = file_result["search_results"]
            response_message = f"🔍 Found {len(results)} file(s) matching '{file_query}' ready for sharing:\n\n"
            
            for i, result in enumerate(results[:3], 1):
                file_info = result["file_info"]
                size_mb = file_info["size"] / (1024 * 1024)
                response_message += f"{i}. 📄 {file_info['name']} ({size_mb:.1f}MB)\n"
            
            if recipient:
                response_message += f"\n💡 Say 'Send [filename] to {recipient} on WhatsApp' to share!"
            else:
                response_message += f"\n💡 Say 'Send [filename] to [contact] on WhatsApp' to share!"
            
            return {
                "success": True,
                "message": response_message,
                "workflow": "search_and_share",
                "search_results": results
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Search and share failed: {str(e)}",
                "workflow": "search_and_share",
                "error": str(e)
            }
    
    def process_command(self, user_input: str) -> Dict[str, Any]:
        """Process user command through MCP workflow with AI enhancement"""
        try:
            # Initialize state with proper structure (including new AI enhancement fields)
            initial_state: AgentManagerState = {
                'user_input': user_input.strip(),
                'original_input': '',  # Will be set by AI enhancement
                'enhanced_input': '',  # Will be set by AI enhancement
                'detected_intent': '',
                'agent_name': '',
                'agent_response': {},
                'final_response': '',
                'error': None
            }
            
            # Run the workflow (now starts with AI enhancement)
            result = self.workflow.invoke(initial_state)
            
            # Ensure all required fields exist in response
            agent_response = result.get('agent_response', {})
            
            # Log enhancement if it happened
            if result.get('original_input') != result.get('enhanced_input'):
                print(f"[DEBUG] ✨ AI Enhancement applied:")
                print(f"[DEBUG]    Original: {result.get('original_input')}")
                print(f"[DEBUG]    Enhanced: {result.get('enhanced_input')}")
            
            return {
                "success": not bool(result.get('error')),
                "message": result.get('final_response', 'Task completed'),
                "intent": result.get('detected_intent', ''),
                "agent_used": result.get('agent_name', ''),
                "agent_response": agent_response,
                "error": result.get('error'),
                # Additional fields for specific agents
                "search_results": agent_response.get('search_results', []),
                "selected_file": agent_response.get('selected_file'),
                "action_type": agent_response.get('action_type'),
                "whatsapp_url": agent_response.get('whatsapp_url'),
                "workflow": agent_response.get('workflow'),
                # AI enhancement tracking
                "original_input": result.get('original_input', user_input),
                "enhanced_input": result.get('enhanced_input', user_input),
                "was_enhanced": result.get('original_input') != result.get('enhanced_input')
            }
            
        except Exception as e:
            error_msg = f"MCP Error: {str(e)}"
            return {
                "success": False,
                "message": f"❌ {error_msg}",
                "intent": "error",
                "agent_used": "none",
                "agent_response": {},
                "error": error_msg,
                "search_results": [],
                "selected_file": None,
                "action_type": "error",
                "whatsapp_url": None,
                "workflow": None,
                "original_input": user_input,
                "enhanced_input": user_input,
                "was_enhanced": False
            }
    
    def get_available_agents(self) -> List[str]:
        """Get list of available agents"""
        return list(self.agents.keys())
    
    def add_agent(self, name: str, agent_instance):
        """Add a new agent to the MCP"""
        self.agents[name] = agent_instance
        # Rebuild workflow when new agents are added
        self.workflow = self._build_workflow()

# Global MCP instance
agent_manager = AgentManager()