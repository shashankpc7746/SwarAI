"""
Feature Request Logger for AI Task Automation Assistant
Tracks unimplemented features requested by users for future development
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

class FeatureRequestLogger:
    """Logs user requests that cannot be fulfilled to JSON file"""
    
    def __init__(self, log_file: str = "feature_requests.json"):
        """
        Initialize feature request logger
        
        Args:
            log_file: Path to JSON log file (relative to backend directory)
        """
        # Get backend directory path
        backend_dir = Path(__file__).parent.parent
        self.log_file = backend_dir / log_file
        
        # Create file if it doesn't exist
        if not self.log_file.exists():
            self._initialize_log_file()
    
    def _initialize_log_file(self):
        """Create initial empty log file"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2, ensure_ascii=False)
            print(f"[INFO] Created feature request log: {self.log_file}")
        except Exception as e:
            print(f"[ERROR] Failed to create feature request log: {e}")
    
    def log_request(
        self,
        user_input: str,
        detected_intent: str = "unknown",
        reason: str = "No matching agent found",
        suggested_agent: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Log an unimplemented feature request
        
        Args:
            user_input: The original user command
            detected_intent: What intent was detected (if any)
            reason: Why the request couldn't be fulfilled
            suggested_agent: Suggested agent name for implementation
            context: Additional context (enhanced input, keywords, etc.)
        
        Returns:
            bool: True if logged successfully, False otherwise
        """
        try:
            # Load existing requests
            requests = self._load_requests()
            
            # Create new request entry
            new_request = {
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input,
                "detected_intent": detected_intent,
                "reason": reason,
                "suggested_agent": suggested_agent,
                "context": context or {},
                "status": "pending",
                "id": len(requests) + 1
            }
            
            # Add to requests
            requests.append(new_request)
            
            # Save to file
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(requests, f, indent=2, ensure_ascii=False)
            
            print(f"\n[FEATURE REQUEST LOGGED]")
            print(f"ID: {new_request['id']}")
            print(f"Input: {user_input}")
            print(f"Reason: {reason}")
            print(f"Suggested: {suggested_agent or 'N/A'}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to log feature request: {e}")
            return False
    
    def _load_requests(self) -> List[Dict[str, Any]]:
        """Load existing feature requests from file"""
        try:
            if self.log_file.exists():
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"[ERROR] Failed to load feature requests: {e}")
            return []
    
    def get_all_requests(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all feature requests, optionally filtered by status
        
        Args:
            status: Filter by status (pending, implemented, rejected)
        
        Returns:
            List of feature request dictionaries
        """
        requests = self._load_requests()
        
        if status:
            requests = [r for r in requests if r.get('status') == status]
        
        return requests
    
    def get_pending_count(self) -> int:
        """Get count of pending feature requests"""
        return len(self.get_all_requests(status="pending"))
    
    def mark_implemented(self, request_id: int) -> bool:
        """
        Mark a feature request as implemented
        
        Args:
            request_id: ID of the request to mark
        
        Returns:
            bool: True if updated successfully
        """
        try:
            requests = self._load_requests()
            
            for req in requests:
                if req.get('id') == request_id:
                    req['status'] = 'implemented'
                    req['implemented_at'] = datetime.now().isoformat()
                    break
            
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(requests, f, indent=2, ensure_ascii=False)
            
            print(f"[INFO] Marked request #{request_id} as implemented")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to mark request as implemented: {e}")
            return False
    
    def generate_summary(self) -> Dict[str, Any]:
        """
        Generate summary of feature requests
        
        Returns:
            Dictionary with statistics and top requests
        """
        requests = self._load_requests()
        
        summary = {
            "total_requests": len(requests),
            "pending": len([r for r in requests if r.get('status') == 'pending']),
            "implemented": len([r for r in requests if r.get('status') == 'implemented']),
            "rejected": len([r for r in requests if r.get('status') == 'rejected']),
            "recent_requests": sorted(requests, key=lambda x: x['timestamp'], reverse=True)[:5]
        }
        
        # Count suggested agents
        agent_suggestions = {}
        for req in requests:
            agent = req.get('suggested_agent')
            if agent:
                agent_suggestions[agent] = agent_suggestions.get(agent, 0) + 1
        
        summary['top_suggested_agents'] = sorted(
            agent_suggestions.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return summary
    
    def get_user_message(self, user_input: str) -> str:
        """
        Generate user-friendly message for unimplemented feature
        
        Args:
            user_input: The user's request
        
        Returns:
            User-friendly message string
        """
        pending_count = self.get_pending_count()
        
        messages = [
            f"🚧 This feature is not implemented yet. Your request has been logged for future development.",
            f"📝 I can't do that right now, but I've saved your request. We have {pending_count} features in the pipeline!",
            f"⚠️ This capability isn't available yet, but your feedback helps us improve! Request logged.",
            f"💡 That's a great idea! I've logged your request for the development team to review.",
        ]
        
        # Rotate messages based on request count
        return messages[pending_count % len(messages)]

# Global logger instance
feature_logger = FeatureRequestLogger()
