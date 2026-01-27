"""
Payment Agent for AI Task Automation Assistant
Opens payment apps with pre-filled payment details
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

class PaymentRequest(BaseModel):
    """Payment request structure"""
    recipient: str
    amount: float
    currency: str = "USD"
    note: str = ""
    app: str = "paypal"  # paypal, googlepay, paytm, phonepe

class AgentState(TypedDict):
    """State for the Payment agent workflow"""
    user_input: str
    parsed_command: Dict[str, Any]
    payment_url: str
    response_message: str
    error: Optional[str]

class PaymentTool(BaseTool):
    """Tool to initiate payments via various apps"""
    name: str = "payment_initiator"
    description: str = "Open payment app with pre-filled payment details"
    
    def _run(self, recipient: str, amount: float, app: str = "paypal", note: str = "", currency: str = "USD") -> str:
        """Initiate payment via specified app"""
        try:
            app = app.lower()
            
            if app == "paypal":
                return self._open_paypal(recipient, amount, note, currency)
            elif app == "googlepay":
                return self._open_googlepay(recipient, amount, note)
            elif app in ["paytm", "phonepe"]:
                return self._open_upi_app(app, recipient, amount, note)
            else:
                # Default to PayPal
                return self._open_paypal(recipient, amount, note, currency)
                
        except Exception as e:
            return f"Error initiating payment: {str(e)}"
    
    def _open_paypal(self, recipient: str, amount: float, note: str, currency: str) -> str:
        """Open PayPal with payment details"""
        # PayPal.me URL format
        paypal_url = f"https://www.paypal.me/{recipient}/{amount}{currency}"
        
        if note:
            paypal_url += f"?note={urllib.parse.quote(note)}"
        
        webbrowser.open(paypal_url)
        return f"PayPal opened for ${amount} to {recipient}"
    
    def _open_googlepay(self, recipient: str, amount: float, note: str) -> str:
        """Open Google Pay"""
        # Google Pay uses UPI format on mobile, web version for desktop
        gpay_url = f"https://pay.google.com/send/home"
        
        webbrowser.open(gpay_url)
        return f"Google Pay opened (manually enter ${amount} to {recipient})"
    
    def _open_upi_app(self, app: str, recipient: str, amount: float, note: str) -> str:
        """Open UPI apps (Paytm, PhonePe)"""
        # UPI deep link format: upi://pay?pa=recipient@upi&pn=Name&am=amount&tn=note
        
        # Extract UPI ID or phone number
        if "@" in recipient:
            upi_id = recipient
        else:
            # Assume it's a phone number
            upi_id = f"{recipient}@paytm"  # Default UPI handle
        
        upi_url = f"upi://pay?pa={upi_id}&am={amount}"
        
        if note:
            upi_url += f"&tn={urllib.parse.quote(note)}"
        
        system = platform.system()
        
        if system == "Windows":
            # Open in browser as fallback
            web_url = f"https://paytm.com" if app == "paytm" else f"https://phonepe.com"
            webbrowser.open(web_url)
        else:
            webbrowser.open(upi_url)
        
        return f"{app.capitalize()} opened for ₹{amount} to {recipient}"

class PaymentAgent:
    """LangGraph-powered Payment Agent"""
    
    def __init__(self):
        # Initialize LLM
        self.llm = ChatGroq(
            groq_api_key=config.GROQ_API_KEY,
            model_name=config.GROQ_MODEL,
            temperature=config.AGENT_TEMPERATURE,
            max_tokens=config.MAX_RESPONSE_TOKENS
        )
        
        # Initialize tools
        self.payment_tool = PaymentTool()
        self.tools = [self.payment_tool]
        
        # Build LangGraph workflow
        self.workflow = self._build_workflow()
        
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for payments"""
        
        def parse_command_node(state: AgentState) -> AgentState:
            """Parse user command to extract payment details"""
            try:
                user_input = state['user_input']
                
                # Use LLM to extract payment components
                system_msg = SystemMessage(content="""You are a payment parsing assistant. Extract the following from the user's command:
                - recipient: person/entity to pay
                - amount: payment amount (numeric value)
                - currency: currency code (USD, INR, EUR, etc.)
                - note: payment note/description
                - app: payment app to use (paypal, googlepay, paytm, phonepe)
                
                Return ONLY a JSON object with these fields. If not mentioned, use defaults.""")
                
                human_msg = HumanMessage(content=f"Parse this payment command: {user_input}")
                
                response = self.llm.invoke([system_msg, human_msg])
                
                # Try to parse JSON from response
                import json
                try:
                    parsed = json.loads(response.content)
                except:
                    # Fallback parsing
                    parsed = {
                        "recipient": self._extract_recipient(user_input),
                        "amount": self._extract_amount(user_input),
                        "currency": self._extract_currency(user_input),
                        "note": self._extract_note(user_input),
                        "app": self._extract_app(user_input)
                    }
                
                state['parsed_command'] = parsed
                state['error'] = None
                
            except Exception as e:
                state['error'] = f"Failed to parse payment command: {str(e)}"
                state['parsed_command'] = {}
                
            return state
        
        def initiate_payment_node(state: AgentState) -> AgentState:
            """Initiate payment via selected app"""
            try:
                if state.get('error'):
                    return state
                
                parsed = state['parsed_command']
                recipient = parsed.get('recipient', '')
                amount = float(parsed.get('amount', 0))
                app = parsed.get('app', 'paypal')
                note = parsed.get('note', '')
                currency = parsed.get('currency', 'USD')
                
                if not recipient or amount <= 0:
                    state['error'] = "Invalid payment details"
                    return state
                
                # Initiate payment
                result = self.payment_tool._run(recipient, amount, app, note, currency)
                
                state['payment_url'] = f"payment_{app}_{recipient}"
                state['response_message'] = f"✅ {result}"
                state['error'] = None
                
            except Exception as e:
                state['error'] = f"Failed to initiate payment: {str(e)}"
                state['response_message'] = "❌ Failed to process payment"
                
            return state
        
        # Build workflow graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("parse_command", parse_command_node)
        workflow.add_node("initiate_payment", initiate_payment_node)
        
        # Add edges
        workflow.set_entry_point("parse_command")
        workflow.add_edge("parse_command", "initiate_payment")
        workflow.add_edge("initiate_payment", END)
        
        return workflow.compile()
    
    def _extract_recipient(self, text: str) -> str:
        """Extract payment recipient from text"""
        patterns = [
            r'(?:pay|send|transfer)\s+(?:to|)\s*([A-Za-z0-9@._-]+)',
            r'(?:recipient|beneficiary)\s+([A-Za-z0-9@._-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_amount(self, text: str) -> float:
        """Extract payment amount from text"""
        # Look for currency symbols and amounts
        patterns = [
            r'[\$₹€£]?\s*(\d+(?:\.\d{2})?)',
            r'(\d+(?:\.\d{2})?)\s*(?:dollars|rupees|euros|pounds)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    return float(match.group(1))
                except:
                    pass
        
        return 0.0
    
    def _extract_currency(self, text: str) -> str:
        """Extract currency from text"""
        text_lower = text.lower()
        
        if '$' in text or 'dollar' in text_lower or 'usd' in text_lower:
            return 'USD'
        elif '₹' in text or 'rupee' in text_lower or 'inr' in text_lower:
            return 'INR'
        elif '€' in text or 'euro' in text_lower or 'eur' in text_lower:
            return 'EUR'
        elif '£' in text or 'pound' in text_lower or 'gbp' in text_lower:
            return 'GBP'
        
        return 'USD'
    
    def _extract_note(self, text: str) -> str:
        """Extract payment note from text"""
        note_pattern = r'(?:for|note|memo)\s+["\']?([^"\']+)["\']?'
        match = re.search(note_pattern, text.lower())
        if match:
            return match.group(1).strip()
        return ""
    
    def _extract_app(self, text: str) -> str:
        """Extract payment app from text"""
        text_lower = text.lower()
        
        if 'paypal' in text_lower:
            return 'paypal'
        elif 'google pay' in text_lower or 'googlepay' in text_lower or 'gpay' in text_lower:
            return 'googlepay'
        elif 'paytm' in text_lower:
            return 'paytm'
        elif 'phonepe' in text_lower or 'phone pe' in text_lower:
            return 'phonepe'
        
        return 'paypal'  # Default
    
    def process_command(self, user_input: str) -> Dict[str, Any]:
        """Process payment command and return result"""
        try:
            initial_state = {
                "user_input": user_input,
                "parsed_command": {},
                "payment_url": "",
                "response_message": "",
                "error": None
            }
            
            # Run workflow
            final_state = self.workflow.invoke(initial_state)
            
            return {
                "success": final_state.get('error') is None,
                "message": final_state.get('response_message', 'Payment processed'),
                "payment_url": final_state.get('payment_url', ''),
                "details": final_state.get('parsed_command', {})
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Payment agent error: {str(e)}",
                "payment_url": "",
                "details": {}
            }

# Create global instance
payment_agent = PaymentAgent()
