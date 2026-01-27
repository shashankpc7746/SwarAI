"""
Multi-Task Workflow Orchestrator for AI Task Automation Assistant
Chains multiple agents together to handle complex multi-step tasks
"""

import re
from typing import Dict, Any, List, Optional, TypedDict
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from config import config

class WorkflowState(TypedDict):
    """State for multi-task workflow"""
    user_input: str
    tasks: List[Dict[str, Any]]
    current_task_index: int
    task_results: List[Dict[str, Any]]
    final_response: str
    error: Optional[str]

class MultiTaskOrchestrator:
    """Orchestrates multi-agent workflows for complex tasks"""
    
    def __init__(self, agent_manager):
        """
        Initialize orchestrator
        
        Args:
            agent_manager: Reference to AgentManager for agent routing
        """
        self.agent_manager = agent_manager
        
        # Initialize LLM for task parsing
        self.llm = ChatGroq(
            groq_api_key=config.GROQ_API_KEY,
            model_name=config.GROQ_MODEL,
            temperature=config.AGENT_TEMPERATURE,
            max_tokens=config.MAX_RESPONSE_TOKENS
        )
    
    def detect_multi_task(self, user_input: str) -> bool:
        """
        Detect if input requires multiple agents
        
        Args:
            user_input: User command
        
        Returns:
            bool: True if multi-task detected
        """
        user_input_lower = user_input.lower()
        
        # Patterns indicating multi-task workflows
        multi_task_patterns = [
            # File + Communication
            r"(find|search|open|get).*(?:file|document|pdf|photo).*(?:send|share|email|whatsapp)",
            r"(send|share|email|whatsapp).*(file|document|pdf|photo)",
            
            # Screenshot + Communication
            r"(take|capture).*screenshot.*(?:send|share|email|whatsapp)",
            r"screenshot.*(?:and|then).*(?:send|share|email)",
            
            # Sequential actions with "and then" or "and"
            r".*\s+and\s+(then\s+)?(?:send|email|call|message|whatsapp)",
            
            # Multiple actions explicitly stated
            r"(first|then|after that|next)",
        ]
        
        # Check patterns
        for pattern in multi_task_patterns:
            if re.search(pattern, user_input_lower):
                return True
        
        # Check for multiple agent keywords
        agent_keywords = {
            "filesearch": ["find", "search", "file", "document", "pdf", "photo"],
            "whatsapp": ["whatsapp", "message", "send message"],
            "email": ["email", "send email", "mail"],
            "screenshot": ["screenshot", "capture screen", "take screenshot"],
            "phone": ["call", "phone", "dial"],
        }
        
        detected_agents = []
        for agent, keywords in agent_keywords.items():
            if any(keyword in user_input_lower for keyword in keywords):
                detected_agents.append(agent)
        
        # If 2+ agents detected, it's multi-task
        return len(detected_agents) >= 2
    
    def parse_workflow(self, user_input: str) -> List[Dict[str, Any]]:
        """
        Parse user input into sequence of tasks
        
        Args:
            user_input: User command
        
        Returns:
            List of task dictionaries with agent and params
        """
        try:
            user_input_lower = user_input.lower()
            tasks = []
            
            # Pattern: "send [file] to [contact]"
            # Example: "send apple.pdf to jay on whatsapp"
            if re.search(r"(send|share).*(file|pdf|photo|document).*(to|with)", user_input_lower):
                # Task 1: Find the file
                file_match = re.search(r"(send|share)\s+(.*?)\s+(?:to|with|on)", user_input)
                if file_match:
                    file_query = file_match.group(2)
                    tasks.append({
                        "agent": "filesearch",
                        "input": f"find {file_query}",
                        "extract": "file_path"
                    })
                
                # Task 2: Send via WhatsApp or Email
                if "whatsapp" in user_input_lower:
                    # Extract contact name - handle both "to Jay" and "Jay on WhatsApp"
                    contact_match = re.search(r"(?:to|with)\s+(\w+)(?:\s+on|\s+via|\s+through)?", user_input, re.IGNORECASE)
                    if contact_match:
                        contact = contact_match.group(1)
                        tasks.append({
                            "agent": "whatsapp",
                            "input": f"send whatsapp to {contact}",
                            "use_previous": "file_path"
                        })
                    else:
                        print(f"[WARNING] WhatsApp contact not found in: {user_input}")
                elif "email" in user_input_lower:
                    contact_match = re.search(r"(?:to|with)\s+([\w\s@.]+)", user_input, re.IGNORECASE)
                    if contact_match:
                        contact = contact_match.group(1)
                        tasks.append({
                            "agent": "email",
                            "input": f"send email to {contact}",
                            "use_previous": "file_path"
                        })
            
            # Pattern: "take screenshot and [action]"
            # Example: "take screenshot and email it to jay"
            elif re.search(r"(take|capture).*screenshot.*(and|then)", user_input_lower):
                # Task 1: Take screenshot
                tasks.append({
                    "agent": "screenshot",
                    "input": "take screenshot",
                    "extract": "screenshot_path"
                })
                
                # Task 2: Share via email/whatsapp
                if "email" in user_input_lower:
                    contact_match = re.search(r"(?:to|with)\s+([\w\s@.]+)", user_input, re.IGNORECASE)
                    if contact_match:
                        contact = contact_match.group(1)
                        tasks.append({
                            "agent": "email",
                            "input": f"send email to {contact}",
                            "use_previous": "screenshot_path"
                        })
                elif "whatsapp" in user_input_lower:
                    # Extract contact name - handle "to Jay" and "Jay on WhatsApp"
                    contact_match = re.search(r"(?:to|with)\s+(\w+)(?:\s+on|\s+via)?", user_input, re.IGNORECASE)
                    if contact_match:
                        contact = contact_match.group(1)
                        tasks.append({
                            "agent": "whatsapp",
                            "input": f"send whatsapp to {contact}",
                            "use_previous": "screenshot_path"
                        })
            
            # If no specific pattern matched, use AI to parse
            if not tasks:
                tasks = self._ai_parse_workflow(user_input)
            
            return tasks
            
        except Exception as e:
            print(f"[ERROR] Failed to parse workflow: {e}")
            return []
    
    def _ai_parse_workflow(self, user_input: str) -> List[Dict[str, Any]]:
        """Use AI to parse complex workflows"""
        try:
            system_msg = SystemMessage(content="""You are a workflow parser. Break down user commands into sequential tasks.
            
Return a JSON array of tasks with this format:
[
  {"agent": "filesearch", "input": "find apple.pdf", "extract": "file_path"},
  {"agent": "whatsapp", "input": "send to Jay", "use_previous": "file_path"}
]

Available agents: filesearch, whatsapp, email, screenshot, phone, calendar, payment, app_launcher, websearch, task

Rules:
- Extract clear, actionable commands for each agent
- Use "extract" to capture output for next task
- Use "use_previous" to reference previous task output
- Keep tasks simple and focused
""")
            
            user_msg = HumanMessage(content=f"Parse this command: {user_input}")
            
            response = self.llm.invoke([system_msg, user_msg])
            
            # Parse AI response (would need better parsing in production)
            # For now, return empty - we handle common patterns above
            return []
            
        except Exception as e:
            print(f"[ERROR] AI workflow parsing failed: {e}")
            return []
    
    def execute_workflow(self, user_input: str) -> Dict[str, Any]:
        """
        Execute multi-task workflow
        
        Args:
            user_input: User command
        
        Returns:
            Workflow execution result
        """
        try:
            # Parse into tasks
            tasks = self.parse_workflow(user_input)
            
            if not tasks:
                return {
                    "success": False,
                    "message": "Could not parse multi-task workflow",
                    "error": "No tasks extracted"
                }
            
            print(f"\n[WORKFLOW] Starting {len(tasks)}-task workflow:")
            for i, task in enumerate(tasks, 1):
                print(f"  Task {i}: {task['agent']} - {task['input']}")
            
            # Execute tasks sequentially
            task_results = []
            shared_data = {}  # Data passed between tasks
            
            for i, task in enumerate(tasks):
                print(f"\n[WORKFLOW] Executing task {i+1}/{len(tasks)}: {task['agent']}")
                
                # Build task input
                task_input = task['input']
                
                # Inject previous task data if needed
                if task.get('use_previous'):
                    prev_key = task['use_previous']
                    if prev_key in shared_data:
                        task_input += f" {shared_data[prev_key]}"
                
                # Execute via agent manager
                agent_name = task['agent']
                if agent_name in self.agent_manager.agents:
                    agent = self.agent_manager.agents[agent_name]
                    result = agent.process_command(task_input)
                    
                    # Store result
                    task_results.append({
                        "task_index": i,
                        "agent": agent_name,
                        "result": result
                    })
                    
                    # Extract data for next task
                    if task.get('extract'):
                        extract_key = task['extract']
                        # Simple extraction - would need better logic
                        if 'file_path' in extract_key and result.get('success'):
                            shared_data[extract_key] = result.get('file_path', '')
                        elif 'screenshot_path' in extract_key and result.get('success'):
                            shared_data[extract_key] = result.get('path', '')
                    
                    # If task failed, stop workflow
                    if not result.get('success'):
                        return {
                            "success": False,
                            "message": f"Workflow failed at task {i+1}: {result.get('message')}",
                            "completed_tasks": i,
                            "task_results": task_results
                        }
            
            # All tasks completed successfully
            return {
                "success": True,
                "message": f"✅ Completed {len(tasks)}-task workflow successfully!",
                "tasks_count": len(tasks),
                "task_results": task_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Workflow execution error: {str(e)}",
                "error": str(e)
            }

# Note: This orchestrator will be initialized by AgentManager with self reference
