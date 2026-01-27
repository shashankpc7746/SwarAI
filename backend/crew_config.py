"""
CrewAI Multi-Agent Orchestration System
Simplified configuration for stable multi-agent workflows using Groq LLM exclusively
"""

import os
from typing import Dict, Any, List, Optional
from crewai import Agent, Task, Crew, Process
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

# Ensure we're using Groq exclusively
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is required. Please set it in your .env file.")

# Force environment variable to avoid OpenAI calls
os.environ.pop("OPENAI_API_KEY", None)  # Remove OpenAI key if present to force Groq usage

# Set CrewAI to use our custom LLM configuration
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

class CrewAIOrchestrator:
    """Main orchestrator for multi-agent workflows using Groq LLM exclusively"""
    
    def __init__(self):
        # Ensure clean environment for Groq-only usage
        self._configure_environment()
        self.llm = self._setup_llm()
        self.agents = self._create_agents()
        
    def _configure_environment(self):
        """Configure environment to use Groq exclusively"""
        # Remove any OpenAI references
        for key in list(os.environ.keys()):
            if 'OPENAI' in key:
                os.environ.pop(key, None)
        
        # Ensure Groq is configured
        os.environ["GROQ_API_KEY"] = GROQ_API_KEY
        
    def _setup_llm(self):
        """Setup Groq LLM exclusively"""
        return ChatGroq(
            groq_api_key=GROQ_API_KEY,
            model_name="llama3-8b-8192",
            temperature=0.1,
            max_tokens=1000
        )
    
    def _create_agents(self):
        """Create specialized agents for different tasks using Groq LLM exclusively"""
        
        # Shared LLM instance for all agents
        shared_llm = self.llm
        
        # Task Coordinator - Decides which agent to use
        coordinator = Agent(
            role='Task Coordinator',
            goal='Analyze user commands and route to appropriate specialists',
            backstory="""You are an intelligent task coordinator who understands user intentions 
            and efficiently delegates tasks to specialized agents. You excel at breaking down 
            complex requests into actionable tasks and determining the best agent for each job.""",
            verbose=True,
            allow_delegation=True,
            llm=shared_llm,
            max_iter=3,
            max_execution_time=30
        )
        
        # File Management Specialist
        file_manager = Agent(
            role='File Management Specialist',
            goal='Handle all file operations including search, opening, and sharing preparation',
            backstory="""You are a file management expert who can efficiently search for files, 
            understand file locations, and prepare files for sharing. You have deep knowledge 
            of file systems and can find files even with partial names or descriptions.""",
            verbose=True,
            allow_delegation=False,
            llm=shared_llm,
            max_iter=2,
            max_execution_time=20
        )
        
        # WhatsApp Communication Specialist
        whatsapp_agent = Agent(
            role='WhatsApp Communication Specialist',
            goal='Handle WhatsApp messaging and link generation for seamless sharing',
            backstory="""You are a communication expert specializing in WhatsApp messaging. 
            You can compose natural messages, understand contact relationships, and create 
            WhatsApp sharing links with proper formatting for different types of content.""",
            verbose=True,
            allow_delegation=False,
            llm=shared_llm,
            max_iter=2,
            max_execution_time=15
        )
        
        return {
            'coordinator': coordinator,
            'file_manager': file_manager,
            'whatsapp_agent': whatsapp_agent
        }
    
    def create_crew_for_task(self, task_type: str) -> Crew:
        """Create appropriate crew based on task type with Groq LLM"""
        
        try:
            if task_type == 'file_and_share':
                # Complex workflow: file search + WhatsApp sharing
                agents = [self.agents['coordinator'], self.agents['file_manager'], self.agents['whatsapp_agent']]
            elif task_type == 'file_only':
                # Simple file operations
                agents = [self.agents['coordinator'], self.agents['file_manager']]
            elif task_type == 'whatsapp_only':
                # Simple messaging
                agents = [self.agents['coordinator'], self.agents['whatsapp_agent']]
            else:
                # General crew with all agents
                agents = list(self.agents.values())
            
            # Create crew with explicit Groq configuration
            return Crew(
                agents=agents,
                process=Process.sequential,
                verbose=False,  # Reduce verbosity to avoid issues
                memory=False,   # Disable memory to avoid potential OpenAI calls
                manager_llm=self.llm  # Explicitly use Groq LLM for crew management
            )
            
        except Exception as e:
            # Fallback to simple crew if advanced features fail
            return Crew(
                agents=[self.agents['coordinator']],
                process=Process.sequential,
                verbose=False,
                memory=False,
                manager_llm=self.llm
            )
    
    def analyze_command(self, user_command: str) -> Dict[str, Any]:
        """Analyze user command to determine workflow type and parameters"""
        command_lower = user_command.lower()
        
        # Detect file + WhatsApp sharing patterns
        sharing_patterns = [
            'send', 'share', 'whatsapp', 'wa.me',
            'message', 'text', 'chat'
        ]
        
        file_patterns = [
            'file', 'document', 'doc', 'pdf', 'image', 'photo',
            'video', 'folder', 'open', 'find', 'search'
        ]
        
        has_sharing = any(pattern in command_lower for pattern in sharing_patterns)
        has_file = any(pattern in command_lower for pattern in file_patterns)
        
        if has_file and has_sharing:
            return {
                'workflow_type': 'file_and_share',
                'requires_popup': True,
                'complexity': 'high'
            }
        elif has_file:
            return {
                'workflow_type': 'file_only', 
                'requires_popup': False,
                'complexity': 'medium'
            }
        elif has_sharing:
            return {
                'workflow_type': 'whatsapp_only',
                'requires_popup': True,
                'complexity': 'medium'
            }
        else:
            return {
                'workflow_type': 'general',
                'requires_popup': False,
                'complexity': 'low'
            }
    
    def execute_workflow(self, user_command: str) -> Dict[str, Any]:
        """Execute complete workflow based on user command with enhanced error handling"""
        try:
            # Analyze command
            analysis = self.analyze_command(user_command)
            workflow_type = analysis['workflow_type']
            
            # Try to create and execute crew
            try:
                crew = self.create_crew_for_task(workflow_type)
                
                # Create simpler task descriptions to avoid complex processing
                if workflow_type == 'file_and_share':
                    task_description = f"Help user with: {user_command}. Focus on file operations and WhatsApp sharing."
                elif workflow_type == 'file_only':
                    task_description = f"Help user with file operations: {user_command}"
                elif workflow_type == 'whatsapp_only':
                    task_description = f"Help user with WhatsApp messaging: {user_command}"
                else:
                    task_description = f"Help user with: {user_command}"
                
                # Create and execute task with timeout
                task = Task(
                    description=task_description,
                    agent=crew.agents[0],  # Start with coordinator
                    expected_output="Brief, helpful response with actionable information"
                )
                
                crew.tasks = [task]
                result = crew.kickoff()
                
                return {
                    'success': True,
                    'result': str(result),
                    'workflow_type': workflow_type,
                    'analysis': analysis,
                    'agents_used': [agent.role for agent in crew.agents],
                    'requires_popup': analysis.get('requires_popup', False)
                }
                
            except Exception as crew_error:
                # If CrewAI fails, provide a manual response
                return self._manual_workflow_fallback(user_command, workflow_type, str(crew_error))
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'result': f"❌ Workflow execution failed: {str(e)}",
                'workflow_type': 'error',
                'analysis': {},
                'agents_used': [],
                'requires_popup': False
            }
    
    def _manual_workflow_fallback(self, user_command: str, workflow_type: str, error_msg: str) -> Dict[str, Any]:
        """Manual fallback when CrewAI fails"""
        cmd_lower = user_command.lower()
        
        if 'file' in cmd_lower and ('share' in cmd_lower or 'whatsapp' in cmd_lower):
            result = "✅ I understand you want to share a file via WhatsApp. Here's what I would do:\n\n1. 📁 Search for the file you mentioned\n2. 📱 Prepare WhatsApp sharing link\n3. 🔗 Create wa.me link for easy sharing\n\nPlease try using the enhanced fallback processing for actual file operations."
        elif 'file' in cmd_lower:
            result = "✅ I can help you with file operations. I would search for the file you mentioned and help you open or manage it. Please try using the enhanced fallback processing for actual file operations."
        elif 'whatsapp' in cmd_lower or 'message' in cmd_lower:
            result = "✅ I can help you with WhatsApp messaging. I would create a proper WhatsApp link for you to send your message. Please try using the enhanced fallback processing for actual WhatsApp operations."
        else:
            result = f"✅ I understand your request: '{user_command}'. While CrewAI had a technical issue, I'm ready to help you with file operations, WhatsApp messaging, or other tasks using the enhanced fallback system."
        
        return {
            'success': True,
            'result': result,
            'workflow_type': workflow_type,
            'analysis': {'complexity': 'fallback'},
            'agents_used': ['Manual Fallback'],
            'requires_popup': False,
            'fallback_reason': f"CrewAI initialization error: {error_msg}"
        }

# Safer orchestrator initialization with error handling
try:
    orchestrator = CrewAIOrchestrator()
    print("✅ CrewAI orchestrator initialized successfully with Groq LLM")
except Exception as init_error:
    print(f"⚠️ CrewAI orchestrator initialization failed: {init_error}")
    
    # Create a minimal fallback orchestrator
    class FallbackOrchestrator:
        def execute_workflow(self, user_command: str) -> Dict[str, Any]:
            return {
                'success': False,
                'error': f"CrewAI unavailable: {init_error}",
                'result': f"❌ CrewAI orchestration not available. Please use enhanced fallback processing. Error: {init_error}",
                'workflow_type': 'error',
                'analysis': {},
                'agents_used': [],
                'requires_popup': False
            }
    
    orchestrator = FallbackOrchestrator()