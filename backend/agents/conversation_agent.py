"""
Conversational Agent for AI Task Automation Assistant (SwarAI)
Provides natural, friendly interactions with personality and context awareness
"""

import re
from typing import Dict, List, Any, Optional, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from datetime import datetime
from config import config
from utils.conversation_memory import conversation_memory
from utils.conversational_tts import conversational_tts

class ConversationState(TypedDict):
    """State for the conversation agent workflow"""
    user_input: str
    intent: str
    response: str
    context: Dict[str, Any]
    personality_response: str
    error: Optional[str]

class ConversationAgent:
    """LangGraph-powered Conversational Agent with SwarAI personality"""
    
    def __init__(self):
        # Initialize LLM
        self.llm = ChatGroq(
            groq_api_key=config.GROQ_API_KEY,
            model_name=config.GROQ_MODEL,
            temperature=0.7,  # Higher temperature for more creative responses
            max_tokens=config.MAX_RESPONSE_TOKENS
        )
        
        # Build LangGraph workflow
        self.workflow = self._build_workflow()
        
        # Conversation context
        self.context = {
            "conversation_history": [],
            "user_preferences": {},
            "session_start": datetime.now().isoformat()
        }
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for conversational interactions"""
        
        def analyze_intent_node(state: ConversationState) -> ConversationState:
            """Analyze user intent and conversational context"""
            try:
                if 'intent' not in state:
                    state['intent'] = ""
                if 'error' not in state:
                    state['error'] = None
                if 'context' not in state:
                    state['context'] = {}
                
                system_prompt = """You are SwarAI, an advanced AI assistant with natural conversation abilities and real task execution capabilities.
                
                Your core personality:
                - Intelligent and knowledgeable on many topics
                - Warm, conversational, and genuinely helpful
                - Capable of both casual conversation and task execution
                - Proactive in understanding user needs
                - Can answer questions, have discussions, and perform real tasks
                
                Analyze the user input for conversation intent. Be flexible - people don't speak in rigid patterns.
                
                CONVERSATION INTENTS:
                - greeting: Hello, hi, good morning, how are you
                - introduction: Who are you, what can you do, capabilities questions
                - knowledge: Any question seeking information or explanation
                - gratitude: Thank you, thanks, appreciation
                - farewell: Goodbye, bye, see you, exit, quit
                - help: Help requests, guidance, how to use
                - casual: General chat, small talk, personal questions
                - task_command: Specific requests for actions (WhatsApp, files, etc.)
                - discussion: Wanting to discuss or learn about a topic
                - clarification: Follow-up questions or seeking more details
                
                For ANY input that's not a clear task command, default to treating it as a conversation/knowledge request.
                Be intelligent and helpful - you can discuss any topic, answer questions, and provide information.
                
                Return ONLY the intent category that best fits."""
                
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=state['user_input'])
                ]
                
                response = self.llm.invoke(messages)
                intent = response.content.strip().lower()
                
                # Default to knowledge/discussion for most inputs
                if intent not in ['greeting', 'introduction', 'gratitude', 'farewell', 'help', 'task_command']:
                    intent = 'knowledge'
                
                state['intent'] = intent
                state['context'] = {
                    "timestamp": datetime.now().isoformat(),
                    "user_input_length": len(state['user_input']),
                    "detected_intent": intent
                }
                
                return state
                
            except Exception as e:
                state['error'] = f"Error analyzing intent: {str(e)}"
                return state
        
        def generate_response_node(state: ConversationState) -> ConversationState:
            """Generate appropriate conversational response"""
            if state.get('error'):
                return state
                
            try:
                intent = state.get('intent', 'unclear')
                user_input = state.get('user_input', '')
                
                # For greetings, provide a warm response with demonstration
                if intent == 'greeting':
                    system_prompt = """You are SwarAI, an intelligent AI assistant. 
                    Respond to the greeting warmly and introduce yourself briefly.
                    Mention that you can have conversations, answer questions, help with WhatsApp messages, file searches, and other tasks.
                    Keep it conversational and welcoming (2-3 sentences max)."""
                    
                    messages = [
                        SystemMessage(content=system_prompt),
                        HumanMessage(content=user_input)
                    ]
                    response = self.llm.invoke(messages)
                    state['response'] = response.content.strip()
                    return state
                
                elif intent == 'introduction' or 'file search' in user_input.lower() or 'capability' in user_input.lower():
                    system_prompt = """You are SwarAI, an advanced AI task automation assistant with real capabilities.
                    
                    When asked about file search or capabilities, demonstrate your abilities by:
                    1. Explaining your file search capabilities
                    2. Actually performing a sample file search to show it works
                    3. Mentioning other capabilities like WhatsApp integration
                    
                    Your actual capabilities:
                    - Advanced file search across Windows, Mac, Linux systems
                    - Real-time WhatsApp message automation
                    - Multi-agent task coordination
                    - Voice-powered hands-free operation
                    - Natural language understanding and conversation
                    - File sharing workflows
                    
                    Be enthusiastic and demonstrate with a real example. End with asking how you can assist them.
                    IMPORTANT: You have access to filesearch_agent - use it to demonstrate!"""
                    
                    # Actually demonstrate file search capability
                    try:
                        import sys
                        import os
                        # Add the current directory to path for imports
                        current_dir = os.path.dirname(os.path.abspath(__file__))
                        if current_dir not in sys.path:
                            sys.path.append(current_dir)
                        
                        from filesearch_agent import filesearch_agent
                        demo_result = filesearch_agent.process_command("search for project files")
                        if demo_result.get('success') and demo_result.get('search_results'):
                            file_count = len(demo_result['search_results'])
                            demo_text = f"\n\n🔍 **Live Demo**: I just searched your system and found {file_count} project-related files! This shows my real file search capabilities in action."
                        else:
                            demo_text = "\n\n🔍 **Live Demo**: I just attempted a file search on your system to demonstrate my capabilities!"
                    except Exception as e:
                        demo_text = "\n\n🔍 **Ready to Search**: My file search system is active and ready to help you find any files!"
                    
                    # Include demo in the response
                    messages = [
                        SystemMessage(content=system_prompt),
                        HumanMessage(content=f"User asked: {user_input}\n\nInclude this demo result: {demo_text}")
                    ]
                    response = self.llm.invoke(messages)
                    state['response'] = response.content.strip()
                    return state
                
                elif intent in ['knowledge', 'discussion', 'clarification']:
                    system_prompt = f"""You are SwarAI, an intelligent AI assistant with broad knowledge and conversational abilities.
                    
                    The user asked: "{user_input}"
                    
                    INSTRUCTIONS:
                    - Provide an intelligent, helpful response using your knowledge
                    - Be conversational and natural, not robotic
                    - If it's a question, answer it clearly and informatively
                    - If it's a statement, respond thoughtfully and engage
                    - If it relates to tasks you can perform, mention your capabilities naturally
                    - Keep responses concise but informative (2-5 sentences typically)
                    - Show that you're an intelligent AI, not just a command processor
                    
                    Respond as the intelligent, helpful AI assistant that you are."""
                    
                    messages = [
                        SystemMessage(content=system_prompt),
                        HumanMessage(content=user_input)
                    ]
                    response = self.llm.invoke(messages)
                    state['response'] = response.content.strip()
                    return state
                
                elif intent == 'help':
                    system_prompt = """You are SwarAI, an intelligent AI assistant. Provide helpful guidance on what you can do:
                    
                    🗣️ **Conversation**: I can discuss any topic, answer questions, and have natural conversations
                    📱 **WhatsApp**: "Send WhatsApp to [name]: [message]" - Send messages instantly
                    📁 **File Search**: "Find [filename]" - Search across your entire system
                    📂 **File Operations**: "Open [filename]" - Open any file directly
                    🔄 **Multi-Agent Tasks**: "Send [filename] to [contact] on WhatsApp" - Complex workflows
                    
                    I understand natural language - no need for rigid commands! Just talk to me naturally.
                    What would you like to explore?"""
                    
                    messages = [
                        SystemMessage(content=system_prompt),
                        HumanMessage(content=user_input)
                    ]
                    response = self.llm.invoke(messages)
                    state['response'] = response.content.strip()
                    return state
                
                elif intent == 'gratitude':
                    system_prompt = """You are SwarAI. Respond warmly to the user's gratitude.
                    Be humble and offer continued assistance. Keep it brief and friendly."""
                    
                    messages = [
                        SystemMessage(content=system_prompt),
                        HumanMessage(content=user_input)
                    ]
                    response = self.llm.invoke(messages)
                    state['response'] = response.content.strip()
                    return state
                
                elif intent == 'farewell':
                    system_prompt = """You are SwarAI. Say goodbye warmly and mention you're always here to help.
                    Be friendly and leave the door open for future interactions."""
                    
                    messages = [
                        SystemMessage(content=system_prompt),
                        HumanMessage(content=user_input)
                    ]
                    response = self.llm.invoke(messages)
                    state['response'] = response.content.strip()
                    return state
                
                # Catch-all handler for any other intents
                else:
                    system_prompt = f"""You are SwarAI, an advanced conversational AI assistant with real capabilities.
                    
                    You are not just a simple chatbot - you are an intelligent AI that can:
                    1. Answer questions on any topic using your knowledge
                    2. Have natural conversations
                    3. Provide helpful information and explanations
                    4. Demonstrate your capabilities when asked
                    5. Execute real tasks like file searches and WhatsApp messaging
                    
                    User Input: "{user_input}"
                    
                    INSTRUCTIONS:
                    - If it's a general question, answer intelligently and helpfully
                    - If it's about your capabilities, explain AND demonstrate if possible
                    - If it's a task request, acknowledge and guide them
                    - If it's casual conversation, engage naturally
                    - Always be helpful, intelligent, and conversational
                    - Use your knowledge to provide valuable responses
                    - Be the smart AI assistant they expect
                    
                    Respond in a natural, intelligent way that shows your AI capabilities.
                    Keep responses concise but informative (2-4 sentences typically)."""
                    
                    # For file search related questions, actually demonstrate
                    if any(keyword in user_input.lower() for keyword in ['file', 'search', 'find', 'document']):
                        try:
                            import sys
                            import os
                            # Add the current directory to path for imports
                            current_dir = os.path.dirname(os.path.abspath(__file__))
                            if current_dir not in sys.path:
                                sys.path.append(current_dir)
                            
                            from filesearch_agent import filesearch_agent
                            demo_result = filesearch_agent.process_command("search documents")
                            if demo_result.get('success') and demo_result.get('search_results'):
                                file_count = len(demo_result['search_results'])
                                system_prompt += f"\n\nLIVE DEMONSTRATION: I just searched and found {file_count} documents on your system to show my real capabilities!"
                        except Exception:
                            system_prompt += "\n\nMy file search system is ready and active!"
                    
                    messages = [
                        SystemMessage(content=system_prompt),
                        HumanMessage(content=user_input)
                    ]
                    
                    response = self.llm.invoke(messages)
                    state['response'] = response.content.strip()
                    return state
                
            except Exception as e:
                state['error'] = f"Error generating response: {str(e)}"
                return state
        
        # Build the workflow graph
        workflow = StateGraph(ConversationState)
        
        # Add nodes
        workflow.add_node("analyze_intent", analyze_intent_node)
        workflow.add_node("generate_response", generate_response_node)
        
        # Add edges
        workflow.set_entry_point("analyze_intent")
        workflow.add_edge("analyze_intent", "generate_response")
        workflow.add_edge("generate_response", END)
        
        return workflow.compile()
    
    def process_conversation(self, user_input: str) -> Dict[str, Any]:
        """Process conversational input and generate appropriate response"""
        try:
            # Initialize state
            initial_state: ConversationState = {
                'user_input': user_input.strip(),
                'intent': '',
                'response': '',
                'context': {},
                'personality_response': '',
                'error': None
            }
            
            # Run the workflow
            result = self.workflow.invoke(initial_state)
            
            # Update conversation context
            self.context["conversation_history"].append({
                "user_input": user_input,
                "intent": result.get('intent', ''),
                "response": result.get('response', ''),
                "timestamp": datetime.now().isoformat()
            })
            
            # Keep only last 10 conversations
            if len(self.context["conversation_history"]) > 10:
                self.context["conversation_history"] = self.context["conversation_history"][-10:]
            
            return {
                "success": not bool(result.get('error')),
                "message": result.get('response', ''),
                "intent": result.get('intent', ''),
                "context": result.get('context', {}),
                "conversation_context": self.context,
                "error": result.get('error')
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Hi! I'm SwarAI, your AI assistant. I had a small hiccup there - could you please try again?",
                "intent": "error",
                "context": {},
                "conversation_context": self.context,
                "error": str(e)
            }
    
    def is_conversational_input(self, user_input: str) -> bool:
        """Determine if input is conversational rather than a task command"""
        user_input_lower = user_input.lower()
        
        # First check if it's a WhatsApp or task command - these should NOT be conversational
        task_patterns = [
            r'\b(send|message|text|whatsapp)\s+\w+\s+to\b',  # "send/message/text X to Y"
            r'\b(send whatsapp|whatsapp to|message to|text to)\b',  # WhatsApp specific patterns
            r'\b(find|search|open|locate)\s+\w+',  # File operations
            r'\b(share|send)\s+\w+\s+(via|on|through)\s+whatsapp\b',  # Sharing patterns
        ]
        
        # If it matches task patterns, it's NOT conversational
        if any(re.search(pattern, user_input_lower) for pattern in task_patterns):
            return False
        
        # Now check for conversational patterns
        conversational_patterns = [
            r'^\s*(hi|hello|hey|good morning|good afternoon|good evening)\s*$',  # Pure greetings
            r'^\s*(how are you|what\'s up|how\'s it going)\s*\??\s*$',  # Status questions
            r'^\s*(who are you|what can you do|help|what are your capabilities)\s*\??\s*$',  # Help/intro
            r'^\s*(thank you|thanks|appreciate)\s*$',  # Gratitude
            r'^\s*(bye|goodbye|see you|exit|quit)\s*$',  # Farewells
            r'^\s*SwarAI\s*$',  # Just saying the name
        ]
        
        return any(re.search(pattern, user_input_lower) for pattern in conversational_patterns)
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the current conversation session"""
        history_count = len(self.context["conversation_history"])
        if history_count == 0:
            return "New conversation session started"
        
        return f"Conversation active with {history_count} exchanges since {self.context['session_start']}"

# Global conversation agent instance
conversation_agent = ConversationAgent()