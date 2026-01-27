"""
Task and Reminder Agent for AI Task Automation Assistant
Manages tasks, to-do lists, and reminders
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, TypedDict, ClassVar
from langchain.tools import BaseTool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from config import config

class Task(BaseModel):
    """Task structure"""
    id: str
    title: str
    description: str = ""
    due_date: Optional[str] = None
    priority: str = "medium"  # low, medium, high
    completed: bool = False
    created_at: str = ""

class AgentState(TypedDict):
    """State for the Task agent workflow"""
    user_input: str
    parsed_command: Dict[str, Any]
    action: str  # add, list, complete, delete
    task_data: Optional[Dict[str, Any]]
    response_message: str
    error: Optional[str]

class TaskManagerTool(BaseTool):
    """Tool to manage tasks and reminders"""
    name: str = "task_manager"
    description: str = "Manage tasks, to-do lists, and reminders"
    
    TASKS_FILE: ClassVar[str] = "tasks.json"
    
    def __init__(self):
        super().__init__()
        self._ensure_tasks_file()
    
    def _ensure_tasks_file(self):
        """Ensure tasks file exists"""
        if not os.path.exists(self.TASKS_FILE):
            with open(self.TASKS_FILE, 'w') as f:
                json.dump({"tasks": []}, f)
    
    def _load_tasks(self) -> List[Dict]:
        """Load tasks from file"""
        try:
            with open(self.TASKS_FILE, 'r') as f:
                data = json.load(f)
                return data.get("tasks", [])
        except:
            return []
    
    def _save_tasks(self, tasks: List[Dict]):
        """Save tasks to file"""
        with open(self.TASKS_FILE, 'w') as f:
            json.dump({"tasks": tasks}, f, indent=2)
    
    def _run(self, action: str, task_data: Dict = None) -> str:
        """Perform task management action"""
        try:
            if action == "add":
                return self._add_task(task_data)
            elif action == "list":
                return self._list_tasks(task_data)
            elif action == "complete":
                return self._complete_task(task_data)
            elif action == "delete":
                return self._delete_task(task_data)
            else:
                return f"Unknown action: {action}"
                
        except Exception as e:
            return f"Error managing task: {str(e)}"
    
    def _add_task(self, task_data: Dict) -> str:
        """Add a new task"""
        tasks = self._load_tasks()
        
        # Create new task
        task_id = f"task_{len(tasks) + 1}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        new_task = {
            "id": task_id,
            "title": task_data.get("title", "Untitled Task"),
            "description": task_data.get("description", ""),
            "due_date": task_data.get("due_date"),
            "priority": task_data.get("priority", "medium"),
            "completed": False,
            "created_at": datetime.now().isoformat()
        }
        
        tasks.append(new_task)
        self._save_tasks(tasks)
        
        return f"Task added: {new_task['title']}"
    
    def _list_tasks(self, filters: Dict = None) -> str:
        """List all tasks"""
        tasks = self._load_tasks()
        
        if not tasks:
            return "No tasks found"
        
        # Apply filters
        if filters:
            show_completed = filters.get("show_completed", False)
            priority = filters.get("priority")
            
            if not show_completed:
                tasks = [t for t in tasks if not t.get("completed", False)]
            
            if priority:
                tasks = [t for t in tasks if t.get("priority") == priority]
        else:
            # Default: show only incomplete tasks
            tasks = [t for t in tasks if not t.get("completed", False)]
        
        # Format task list
        task_list = []
        for i, task in enumerate(tasks, 1):
            status = "✓" if task.get("completed") else "○"
            priority = task.get("priority", "medium").upper()
            due = f" (Due: {task.get('due_date')})" if task.get('due_date') else ""
            task_list.append(f"{i}. {status} [{priority}] {task['title']}{due}")
        
        return "\n".join(task_list)
    
    def _complete_task(self, task_data: Dict) -> str:
        """Mark task as completed"""
        tasks = self._load_tasks()
        task_id = task_data.get("task_id")
        task_title = task_data.get("title")
        
        # Find task by ID or title
        for task in tasks:
            if (task_id and task["id"] == task_id) or (task_title and task_title.lower() in task["title"].lower()):
                task["completed"] = True
                self._save_tasks(tasks)
                return f"Task completed: {task['title']}"
        
        return "Task not found"
    
    def _delete_task(self, task_data: Dict) -> str:
        """Delete a task"""
        tasks = self._load_tasks()
        task_id = task_data.get("task_id")
        task_title = task_data.get("title")
        
        # Find and remove task
        for i, task in enumerate(tasks):
            if (task_id and task["id"] == task_id) or (task_title and task_title.lower() in task["title"].lower()):
                removed_task = tasks.pop(i)
                self._save_tasks(tasks)
                return f"Task deleted: {removed_task['title']}"
        
        return "Task not found"

class TaskAgent:
    """LangGraph-powered Task Management Agent"""
    
    def __init__(self):
        # Initialize LLM
        self.llm = ChatGroq(
            groq_api_key=config.GROQ_API_KEY,
            model_name=config.GROQ_MODEL,
            temperature=config.AGENT_TEMPERATURE,
            max_tokens=config.MAX_RESPONSE_TOKENS
        )
        
        # Initialize tools
        self.task_tool = TaskManagerTool()
        self.tools = [self.task_tool]
        
        # Build LangGraph workflow
        self.workflow = self._build_workflow()
        
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for task management"""
        
        def parse_command_node(state: AgentState) -> AgentState:
            """Parse user command to extract task action and data"""
            try:
                user_input = state['user_input']
                
                # Determine action
                action, task_data = self._parse_task_command(user_input)
                
                state['parsed_command'] = task_data
                state['action'] = action
                state['task_data'] = task_data
                state['error'] = None
                
            except Exception as e:
                state['error'] = f"Failed to parse task command: {str(e)}"
                state['parsed_command'] = {}
                state['action'] = ""
                
            return state
        
        def execute_task_action_node(state: AgentState) -> AgentState:
            """Execute task management action"""
            try:
                if state.get('error'):
                    return state
                
                action = state.get('action', '')
                task_data = state.get('task_data', {})
                
                # Execute action
                result = self.task_tool._run(action, task_data)
                
                state['response_message'] = f"✅ {result}"
                state['error'] = None
                
            except Exception as e:
                state['error'] = f"Failed to execute task action: {str(e)}"
                state['response_message'] = "❌ Task action failed"
                
            return state
        
        # Build workflow graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("parse_command", parse_command_node)
        workflow.add_node("execute_action", execute_task_action_node)
        
        # Add edges
        workflow.set_entry_point("parse_command")
        workflow.add_edge("parse_command", "execute_action")
        workflow.add_edge("execute_action", END)
        
        return workflow.compile()
    
    def _parse_task_command(self, text: str) -> tuple:
        """Parse task command to determine action and data"""
        text_lower = text.lower()
        
        # Detect action
        if any(keyword in text_lower for keyword in ["add", "create", "new", "remind me"]):
            action = "add"
            task_data = {
                "title": self._extract_task_title(text),
                "description": text,
                "due_date": self._extract_due_date(text),
                "priority": self._extract_priority(text)
            }
        elif any(keyword in text_lower for keyword in ["list", "show", "what are", "my tasks"]):
            action = "list"
            task_data = {
                "show_completed": "all" in text_lower or "completed" in text_lower,
                "priority": self._extract_priority(text) if "high" in text_lower or "low" in text_lower else None
            }
        elif any(keyword in text_lower for keyword in ["complete", "done", "finish", "mark"]):
            action = "complete"
            task_data = {
                "title": self._extract_task_title(text)
            }
        elif any(keyword in text_lower for keyword in ["delete", "remove", "cancel"]):
            action = "delete"
            task_data = {
                "title": self._extract_task_title(text)
            }
        else:
            action = "list"
            task_data = {}
        
        return (action, task_data)
    
    def _extract_task_title(self, text: str) -> str:
        """Extract task title from text"""
        import re
        
        # Remove action keywords
        cleaned = text
        for keyword in ["add task", "create task", "new task", "remind me to", "complete", "delete", "remove"]:
            cleaned = cleaned.lower().replace(keyword, "")
        
        return cleaned.strip()
    
    def _extract_due_date(self, text: str) -> Optional[str]:
        """Extract due date from text"""
        text_lower = text.lower()
        
        if "tomorrow" in text_lower:
            return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        elif "today" in text_lower:
            return datetime.now().strftime("%Y-%m-%d")
        elif "next week" in text_lower:
            return (datetime.now() + timedelta(weeks=1)).strftime("%Y-%m-%d")
        
        return None
    
    def _extract_priority(self, text: str) -> str:
        """Extract priority from text"""
        text_lower = text.lower()
        
        if "high" in text_lower or "urgent" in text_lower or "important" in text_lower:
            return "high"
        elif "low" in text_lower:
            return "low"
        
        return "medium"
    
    def process_command(self, user_input: str) -> Dict[str, Any]:
        """Process task command and return result"""
        try:
            initial_state = {
                "user_input": user_input,
                "parsed_command": {},
                "action": "",
                "task_data": None,
                "response_message": "",
                "error": None
            }
            
            # Run workflow
            final_state = self.workflow.invoke(initial_state)
            
            return {
                "success": final_state.get('error') is None,
                "message": final_state.get('response_message', 'Task processed'),
                "action": final_state.get('action', ''),
                "details": final_state.get('parsed_command', {})
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Task agent error: {str(e)}",
                "action": "",
                "details": {}
            }

# Create global instance
task_agent = TaskAgent()
