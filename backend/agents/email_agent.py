"""
Email Agent for AI Task Automation Assistant
Opens default email client with pre-filled email details
"""

import webbrowser
import urllib.parse
import subprocess
import platform
import re
from typing import Dict, Any, Optional, TypedDict
from langchain.tools import BaseTool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from config import config

class EmailMessage(BaseModel):
    """Email message structure"""
    recipient: str
    subject: str = ""
    body: str = ""
    cc: Optional[str] = None

class AgentState(TypedDict):
    """State for the Email agent workflow"""
    user_input: str
    parsed_command: Dict[str, Any]
    email_url: str
    response_message: str
    error: Optional[str]

class EmailComposerTool(BaseTool):
    """Tool to compose and open email in default client"""
    name: str = "email_composer"
    description: str = "Open default email client with pre-filled email details"
    
    def _run(self, recipient: str, subject: str = "", body: str = "", cc: str = None) -> str:
        """Open Gmail compose in browser instead of desktop client"""
        try:
            # Build Gmail compose URL instead of mailto
            gmail_base = "https://mail.google.com/mail/?view=cm&fs=1"
            params = []
            
            if recipient:
                params.append(f"to={urllib.parse.quote(recipient)}")
            if subject:
                params.append(f"su={urllib.parse.quote(subject)}")
            if body:
                params.append(f"body={urllib.parse.quote(body)}")
            if cc:
                params.append(f"cc={urllib.parse.quote(cc)}")
            
            gmail_url = gmail_base + "&" + "&".join(params) if params else gmail_base
            
            # Open in default browser
            webbrowser.open(gmail_url)
            
            return f"Gmail compose opened in browser for: {recipient}"
            
        except Exception as e:
            return f"Error opening Gmail: {str(e)}"

class EmailAgent:
    """LangGraph-powered Email Agent"""
    
    def __init__(self):
        # Initialize LLM
        self.llm = ChatGroq(
            groq_api_key=config.GROQ_API_KEY,
            model_name=config.GROQ_MODEL,
            temperature=config.AGENT_TEMPERATURE,
            max_tokens=config.MAX_RESPONSE_TOKENS
        )
        
        # Initialize tools
        self.email_tool = EmailComposerTool()
        self.tools = [self.email_tool]
        
        # Build LangGraph workflow
        self.workflow = self._build_workflow()
        
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for email sending"""
        
        def parse_command_node(state: AgentState) -> AgentState:
            """Parse user command to extract email details"""
            try:
                user_input = state['user_input']
                
                # Use LLM to extract email components
                system_msg = SystemMessage(content="""You are an email parsing assistant. Extract the following from the user's command:
                - recipient: ONLY the person's name or email address (DO NOT include command words like 'draft', 'email', 'to', etc.)
                - subject: email subject (if mentioned)
                - body: email body/message content (if provided)
                - use_ai: true if user wants AI to write/enhance the email (keywords: "ai", "groq", "generate", "write for me", "compose", "draft")
                - context: any additional context for AI to use when generating content
                
                IMPORTANT: For recipient, extract ONLY the name or email, nothing else!
                
                Examples:
                - "send email to jay@email.com subject meeting" -> recipient: "jay@email.com", subject: "meeting", body: "", use_ai: false
                - "draft email to Vijay Sharma about internship" -> recipient: "Vijay Sharma", subject: "internship", use_ai: true
                - "compose email to hr@company.com about application" -> recipient: "hr@company.com", subject: "application", use_ai: true
                - "email Jay regarding project" -> recipient: "Jay", subject: "project", use_ai: true
                
                Return ONLY a JSON object with these fields. If not mentioned, use empty string for text fields and false for use_ai.""")
                
                human_msg = HumanMessage(content=f"Parse this email command: {user_input}")
                
                response = self.llm.invoke([system_msg, human_msg])
                
                # Try to parse JSON from response
                import json
                try:
                    parsed = json.loads(response.content)
                except:
                    # Fallback parsing
                    parsed = {
                        "recipient": self._extract_recipient(user_input),
                        "subject": self._extract_subject(user_input),
                        "body": self._extract_body(user_input),
                        "use_ai": self._detect_ai_request(user_input),
                        "context": user_input
                    }
                
                # Clean up recipient - remove any command words more reliably
                recipient = parsed.get('recipient', '').strip()
                
                # If recipient seems to have command words, clean it
                if recipient:
                    # Remove common command prefixes (case insensitive)
                    # Pattern: "draftanemailtoVijaySharma" -> "VijaySharma"
                    import re
                    
                    # First pass: Remove concatenated command phrases
                    recipient = re.sub(r'^(?:draft|send|compose|write)?(?:an?)?(?:e?mail)?(?:to)?', '', recipient, flags=re.IGNORECASE)
                    
                    # Second pass: Remove word-by-word if still contaminated
                    command_words = ['draft', 'send', 'email', 'compose', 'write', 'mail', 'an', 'to', 'the']
                    recipient_clean = recipient
                    for word in command_words:
                        # Only remove if it's a separate word or at start
                        recipient_clean = re.sub(r'^\s*' + re.escape(word) + r'\s+', '', recipient_clean, flags=re.IGNORECASE)
                        recipient_clean = re.sub(r'\s+' + re.escape(word) + r'\s+', ' ', recipient_clean, flags=re.IGNORECASE)
                    
                    recipient = recipient_clean.strip()
                    
                    # If we cleaned too much (empty or just one char), try fallback extraction
                    if not recipient or len(recipient) < 2:
                        # Try to extract from original input
                        recipient = self._extract_recipient(user_input)
                
                parsed['recipient'] = recipient
                
                print(f"[EMAIL] Parsed command:")
                print(f"  - Original input: '{user_input}'")
                print(f"  - Recipient: '{recipient}'")
                print(f"  - Subject: '{parsed.get('subject', '')}'")
                print(f"  - Use AI: {parsed.get('use_ai', False)}")
                print(f"  - Body preview: '{parsed.get('body', '')[:100]}...' ({len(parsed.get('body', ''))} chars)")
                
                state['parsed_command'] = parsed
                state['error'] = None
                
            except Exception as e:
                state['error'] = f"Failed to parse email command: {str(e)}"
                state['parsed_command'] = {}
                
            return state
        
        def generate_email_content_node(state: AgentState) -> AgentState:
            """Use AI to generate professional email content if requested"""
            try:
                if state.get('error'):
                    return state
                
                parsed = state['parsed_command']
                
                # Always use AI if body is empty OR if explicitly requested
                should_use_ai = parsed.get('use_ai', False) or not parsed.get('body', '').strip()
                
                print(f"[EMAIL] Should use AI: {should_use_ai} (use_ai={parsed.get('use_ai')}, has_body={bool(parsed.get('body', '').strip())})")
                
                # Check if AI content generation is needed
                if should_use_ai:
                    # Generate email body using Groq AI
                    recipient = parsed.get('recipient', '')
                    subject = parsed.get('subject', '')
                    context = parsed.get('context', state['user_input'])
                    
                    print(f"[EMAIL] Generating AI content for: {recipient}, subject: {subject}")
                    
                    # Create prompt for AI to generate email
                    system_msg = SystemMessage(content="""You are a professional email writing assistant. 
                    Generate clear, professional, and concise email content based on the user's requirements.
                    
                    Guidelines:
                    - Keep it professional but friendly
                    - Be concise and to the point (200-400 words max)
                    - Use proper email etiquette (greetings, closing, etc.)
                    - Format with proper paragraphs
                    - Don't include subject line in body (it's separate)
                    - Don't add email headers like "To:", "From:" etc.
                    
                    Return ONLY the email body content, ready to paste.""")
                    
                    human_msg = HumanMessage(content=f"""Generate email body for:
                    Recipient: {recipient}
                    Subject: {subject}
                    Context/Instructions: {context}
                    
                    Write a professional email body that addresses this subject and context.""")
                    
                    try:
                        response = self.llm.invoke([system_msg, human_msg])
                        generated_body = response.content.strip()
                        
                        # Update body with AI-generated content
                        parsed['body'] = generated_body
                        parsed['ai_generated'] = True
                        
                        print(f"[EMAIL] AI generated {len(generated_body)} chars of content")
                        
                    except Exception as e:
                        print(f"[EMAIL] AI body generation failed: {str(e)}")
                        # Continue with empty/existing body
                        parsed['ai_generated'] = False
                    
                    # Also improve subject grammar if present
                    subject = parsed.get('subject', '').strip()
                    if subject and len(subject) > 0:
                        try:
                            subject_prompt = SystemMessage(content="""Improve the grammar and capitalization of this email subject line.
                            
                            Rules:
                            - Capitalize first letter and important words
                            - Fix grammar mistakes
                            - Keep it concise
                            - Don't add extra words
                            
                            Examples:
                            - "application for ai internship" -> "Application for AI Internship"
                            - "meeting tomorrow" -> "Meeting Tomorrow"
                            - "project update" -> "Project Update"
                            
                            Return ONLY the corrected subject line.""")
                            
                            subject_response = self.llm.invoke([subject_prompt, HumanMessage(content=f"Correct this subject: {subject}")])
                            corrected_subject = subject_response.content.strip()
                            
                            # Remove quotes if LLM added them
                            if (corrected_subject.startswith('"') and corrected_subject.endswith('"')) or \
                               (corrected_subject.startswith("'") and corrected_subject.endswith("'")):
                                corrected_subject = corrected_subject[1:-1]
                            
                            parsed['subject'] = corrected_subject
                            print(f"[EMAIL] Subject corrected: '{subject}' -> '{corrected_subject}'")
                            
                        except Exception as e:
                            print(f"[EMAIL] Subject correction failed: {str(e)}")
                            # Keep original subject
                    
                    state['parsed_command'] = parsed
                else:
                    print(f"[EMAIL] Skipping AI generation (body already provided)")
                
            except Exception as e:
                # If AI generation fails completely, continue with whatever we have
                print(f"[EMAIL] Email content generation error: {str(e)}")
                if 'parsed_command' in state:
                    state['parsed_command']['ai_generated'] = False
                
            return state
        
        def compose_email_node(state: AgentState) -> AgentState:
            """Compose and open email"""
            try:
                if state.get('error'):
                    return state
                
                parsed = state['parsed_command']
                recipient = parsed.get('recipient', '').strip()
                subject = parsed.get('subject', '').strip()
                body = parsed.get('body', '').strip()
                ai_generated = parsed.get('ai_generated', False)
                
                # Validate recipient
                if not recipient or len(recipient) < 2:
                    state['error'] = "❌ No valid recipient found. Please specify who to send the email to."
                    state['response_message'] = state['error']
                    return state
                
                print(f"[EMAIL] Opening Gmail for: {recipient}")
                print(f"[EMAIL] Subject: {subject}")
                print(f"[EMAIL] Body length: {len(body)} chars")
                
                # Build Gmail URL with proper encoding
                try:
                    gmail_base = "https://mail.google.com/mail/?view=cm&fs=1"
                    params = []
                    
                    if recipient:
                        params.append(f"to={urllib.parse.quote(recipient, safe='')}")
                    if subject:
                        params.append(f"su={urllib.parse.quote(subject, safe='')}")
                    if body:
                        # Gmail has URL length limits, truncate if too long
                        max_body_length = 5000
                        if len(body) > max_body_length:
                            body = body[:max_body_length] + "\n\n[Content truncated due to length]"
                        params.append(f"body={urllib.parse.quote(body, safe='')}")
                    
                    gmail_url = gmail_base + ("&" + "&".join(params) if params else "")
                    
                    # Open in browser
                    webbrowser.open(gmail_url)
                    print(f"[EMAIL] Gmail URL opened successfully")
                    
                except Exception as e:
                    print(f"[EMAIL] Failed to open Gmail: {str(e)}")
                    state['error'] = f"Failed to open Gmail: {str(e)}"
                    state['response_message'] = "❌ Failed to open Gmail"
                    return state
                
                # Build response message
                response_parts = [f"✅ Gmail compose opened for: {recipient}"]
                if subject:
                    response_parts.append(f"📧 Subject: {subject}")
                if ai_generated and body:
                    response_parts.append(f"🤖 AI-generated email content ready!")
                    # Show preview (limited to 200 chars)
                    if len(body) > 200:
                        response_parts.append(f"📝 Preview: {body[:200]}...")
                    else:
                        response_parts.append(f"📝 Content: {body}")
                elif body:
                    if len(body) > 200:
                        response_parts.append(f"📝 Message: {body[:200]}...")
                    else:
                        response_parts.append(f"📝 Message: {body}")
                
                state['email_url'] = gmail_url
                state['response_message'] = "\n".join(response_parts)
                state['error'] = None
                
            except Exception as e:
                print(f"[EMAIL] Error in compose_email_node: {str(e)}")
                state['error'] = f"Failed to compose email: {str(e)}"
                state['response_message'] = f"❌ Failed to compose email: {str(e)}"
                
            return state
        
        # Build workflow graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("parse_command", parse_command_node)
        workflow.add_node("generate_content", generate_email_content_node)
        workflow.add_node("compose_email", compose_email_node)
        
        # Add edges
        workflow.set_entry_point("parse_command")
        workflow.add_edge("parse_command", "generate_content")
        workflow.add_edge("generate_content", "compose_email")
        workflow.add_edge("compose_email", END)
        
        return workflow.compile()
    
    def _detect_ai_request(self, text: str) -> bool:
        """Detect if user wants AI to generate email content"""
        ai_keywords = ['ai', 'groq', 'generate', 'write', 'compose', 'draft', 'create content', 'write for me']
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in ai_keywords)
    
    def _extract_recipient(self, text: str) -> str:
        """Extract email recipient from text"""
        # Mock email contacts database (in production, this would be from a real contacts API)
        email_contacts = {
            "vijay sharma": "vijaysharma@gmail.com",
            "vijay": "vijaysharma@gmail.com",
            "jay": "jay@email.com",
            "gitanjali": "gitanjali@college.edu",
            "gitanjali mam": "gitanjali@college.edu",
            "shivam": "shivam@email.com",
            "shivam clg": "shivam@email.com",
        }
        
        # Look for email patterns (handle spaces in email addresses)
        # First, try to find emails with potential spaces: "7819 Vijay sharma@gmail.com" -> "7819Vijaysharma@gmail.com"
        email_with_spaces = r'([\w\d\s]+@[\w\d.-]+\.[A-Za-z]{2,})'
        match = re.search(email_with_spaces, text)
        if match:
            # Remove spaces from email
            email = match.group(0).replace(' ', '')
            return email
        
        # Standard email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        if match:
            return match.group(0)
        
        # Look for "to [name]" pattern
        to_pattern = r'(?:to|email)\s+([A-Za-z\s]+?)(?:\s+about|\s+regarding|\s+for|\s+his|\s+her|$)'
        match = re.search(to_pattern, text.lower())
        if match:
            name = match.group(1).strip()
            
            # Try fuzzy matching with contacts
            name_lower = name.lower()
            
            # Exact match
            if name_lower in email_contacts:
                return email_contacts[name_lower]
            
            # Fuzzy match - check if any contact name is in the query
            for contact_name, email in email_contacts.items():
                if contact_name in name_lower or name_lower in contact_name:
                    print(f"[DEBUG] Fuzzy matched '{name}' to '{contact_name}' -> {email}")
                    return email
            
            # No match found, return the name (user can add email manually)
            return name
        
        return ""
    
    def _extract_subject(self, text: str) -> str:
        """Extract email subject from text"""
        subject_pattern = r'(?:subject|about|regarding)\s+[\'"]?([^\'"\n]+)[\'"]?'
        match = re.search(subject_pattern, text.lower())
        if match:
            return match.group(1).strip()
        return ""
    
    def _extract_body(self, text: str) -> str:
        """Extract email body from text"""
        body_pattern = r'(?:body|message|saying|tell)\s+[\'"]?([^\'"\n]+)[\'"]?'
        match = re.search(body_pattern, text.lower())
        if match:
            return match.group(1).strip()
        
        # Fallback: use entire text if no specific pattern
        return text
    
    def process_command(self, user_input: str) -> Dict[str, Any]:
        """Process email command and return result"""
        try:
            initial_state = {
                "user_input": user_input,
                "parsed_command": {},
                "email_url": "",
                "response_message": "",
                "error": None
            }
            
            # Run workflow
            final_state = self.workflow.invoke(initial_state)
            
            return {
                "success": final_state.get('error') is None,
                "message": final_state.get('response_message', 'Email processed'),
                "email_url": final_state.get('email_url', ''),
                "details": final_state.get('parsed_command', {})
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Email agent error: {str(e)}",
                "email_url": "",
                "details": {}
            }

# Create global instance
email_agent = EmailAgent()
