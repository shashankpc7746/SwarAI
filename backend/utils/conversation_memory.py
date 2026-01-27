"""
MongoDB-based Conversation Memory Service
Persistent conversation history and context management for Vaani AI
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import uuid

try:
    from pymongo import MongoClient
    from motor.motor_asyncio import AsyncIOMotorClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

from config import config

logger = logging.getLogger(__name__)

class ConversationMemory:
    """
    Production-level conversation memory with MongoDB persistence
    Handles user context, conversation history, and AI learning
    """
    
    def __init__(self):
        self.config = config
        self.client = None
        self.db = None
        self.conversations = None
        self.user_profiles = None
        self.connected = False
        
        # In-memory fallback
        self.memory_fallback = {
            "conversations": {},
            "user_profiles": {},
            "session_cache": {}
        }
        
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize MongoDB connection"""
        if not MONGODB_AVAILABLE:
            logger.warning("📁 MongoDB not available, using in-memory storage")
            return
        
        try:
            # Try to connect to MongoDB
            self.client = MongoClient(
                self.config.MONGODB_URL,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=5000
            )
            
            # Test connection
            self.client.server_info()
            
            self.db = self.client[self.config.MONGODB_DATABASE]
            self.conversations = self.db.conversations
            self.user_profiles = self.db.user_profiles
            
            # Create indexes for better performance
            self._create_indexes()
            
            self.connected = True
            logger.info("✅ MongoDB connected successfully")
            
        except Exception as e:
            logger.warning(f"⚠️ MongoDB connection failed: {e}. Using in-memory fallback")
            self.connected = False
    
    def _create_indexes(self):
        """Create database indexes for optimal performance"""
        try:
            if self.connected:
                # Conversation indexes
                self.conversations.create_index([("user_id", 1), ("timestamp", -1)])
                self.conversations.create_index([("session_id", 1)])
                self.conversations.create_index([("timestamp", -1)])
                
                # User profile indexes
                self.user_profiles.create_index([("user_id", 1)], unique=True)
                
                logger.info("📊 MongoDB indexes created")
        except Exception as e:
            logger.error(f"Index creation error: {e}")
    
    async def add_conversation_entry(
        self, 
        user_id: str, 
        user_message: str, 
        vaani_response: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add conversation entry with full context"""
        
        conversation_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        
        conversation_entry = {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "session_id": self._get_session_id(user_id),
            "timestamp": timestamp,
            "user_message": user_message,
            "vaani_response": vaani_response,
            "metadata": metadata or {},
            "interaction_type": metadata.get("type", "conversation") if metadata else "conversation",
            "agent_used": metadata.get("agent_used", "conversation") if metadata else "conversation",
            "success": metadata.get("success", True) if metadata else True,
            "response_time_ms": metadata.get("response_time", 0) if metadata else 0
        }
        
        if self.connected:
            try:
                await self._async_insert_conversation(conversation_entry)
            except Exception as e:
                logger.error(f"MongoDB insert error: {e}")
                # Fallback to memory
                self._add_to_memory_fallback(user_id, conversation_entry)
        else:
            self._add_to_memory_fallback(user_id, conversation_entry)
        
        # Update user profile
        await self._update_user_profile(user_id, conversation_entry)
        
        return conversation_id
    
    async def _async_insert_conversation(self, entry: Dict[str, Any]):
        """Async MongoDB insert"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.conversations.insert_one, entry)
    
    def _add_to_memory_fallback(self, user_id: str, entry: Dict[str, Any]):
        """Add to in-memory fallback storage"""
        if user_id not in self.memory_fallback["conversations"]:
            self.memory_fallback["conversations"][user_id] = []
        
        self.memory_fallback["conversations"][user_id].append(entry)
        
        # Keep only recent conversations
        if len(self.memory_fallback["conversations"][user_id]) > self.config.CONVERSATION_MEMORY_LIMIT:
            self.memory_fallback["conversations"][user_id] = \
                self.memory_fallback["conversations"][user_id][-self.config.CONVERSATION_MEMORY_LIMIT:]
    
    async def get_conversation_history(
        self, 
        user_id: str, 
        limit: int = 20,
        include_context: bool = True
    ) -> List[Dict[str, Any]]:
        """Get user's conversation history"""
        
        if self.connected:
            try:
                conversations = await self._async_get_conversations(user_id, limit)
                return conversations
            except Exception as e:
                logger.error(f"MongoDB query error: {e}")
        
        # Fallback to memory
        user_conversations = self.memory_fallback["conversations"].get(user_id, [])
        return list(reversed(user_conversations[-limit:]))
    
    async def _async_get_conversations(self, user_id: str, limit: int) -> List[Dict[str, Any]]:
        """Async MongoDB query"""
        loop = asyncio.get_event_loop()
        cursor = self.conversations.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).limit(limit)
        
        conversations = await loop.run_in_executor(None, list, cursor)
        return list(reversed(conversations))
    
    async def get_conversation_context(self, user_id: str) -> Dict[str, Any]:
        """Get contextual information for better responses"""
        
        recent_conversations = await self.get_conversation_history(user_id, limit=10)
        
        context = {
            "user_id": user_id,
            "conversation_count": len(recent_conversations),
            "recent_topics": [],
            "frequently_used_agents": {},
            "user_preferences": {},
            "last_interaction": None
        }
        
        if recent_conversations:
            context["last_interaction"] = recent_conversations[-1].get("timestamp")
            
            # Analyze recent topics and agents
            for conv in recent_conversations:
                agent = conv.get("agent_used", "unknown")
                if agent in context["frequently_used_agents"]:
                    context["frequently_used_agents"][agent] += 1
                else:
                    context["frequently_used_agents"][agent] = 1
        
        # Get user profile
        user_profile = await self.get_user_profile(user_id)
        if user_profile:
            context["user_preferences"] = user_profile.get("preferences", {})
        
        return context
    
    async def _update_user_profile(self, user_id: str, conversation: Dict[str, Any]):
        """Update user profile based on interaction"""
        
        profile_update = {
            "user_id": user_id,
            "last_interaction": conversation["timestamp"],
            "total_interactions": 1,
            "preferred_agents": {},
            "interaction_patterns": {},
            "preferences": {
                "voice_feedback": True,
                "response_style": "conversational"
            }
        }
        
        if self.connected:
            try:
                await self._async_upsert_profile(user_id, profile_update, conversation)
            except Exception as e:
                logger.error(f"Profile update error: {e}")
        else:
            self._update_memory_profile(user_id, profile_update, conversation)
    
    async def _async_upsert_profile(self, user_id: str, profile: Dict[str, Any], conversation: Dict[str, Any]):
        """Async profile upsert"""
        loop = asyncio.get_event_loop()
        
        # Increment counters
        agent_used = conversation.get("agent_used", "unknown")
        
        await loop.run_in_executor(
            None,
            self.user_profiles.update_one,
            {"user_id": user_id},
            {
                "$set": {
                    "last_interaction": profile["last_interaction"],
                    "user_id": user_id
                },
                "$inc": {
                    "total_interactions": 1,
                    f"preferred_agents.{agent_used}": 1
                },
                "$setOnInsert": {
                    "created_at": datetime.utcnow(),
                    "preferences": profile["preferences"]
                }
            },
            True  # upsert
        )
    
    def _update_memory_profile(self, user_id: str, profile: Dict[str, Any], conversation: Dict[str, Any]):
        """Update in-memory profile"""
        if user_id not in self.memory_fallback["user_profiles"]:
            self.memory_fallback["user_profiles"][user_id] = profile
        else:
            existing = self.memory_fallback["user_profiles"][user_id]
            existing["last_interaction"] = profile["last_interaction"]
            existing["total_interactions"] = existing.get("total_interactions", 0) + 1
            
            agent = conversation.get("agent_used", "unknown")
            if "preferred_agents" not in existing:
                existing["preferred_agents"] = {}
            existing["preferred_agents"][agent] = existing["preferred_agents"].get(agent, 0) + 1
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile"""
        
        if self.connected:
            try:
                loop = asyncio.get_event_loop()
                profile = await loop.run_in_executor(
                    None, 
                    self.user_profiles.find_one, 
                    {"user_id": user_id}
                )
                return profile
            except Exception as e:
                logger.error(f"Profile query error: {e}")
        
        return self.memory_fallback["user_profiles"].get(user_id)
    
    def _get_session_id(self, user_id: str) -> str:
        """Get or create session ID"""
        session_key = f"session_{user_id}"
        
        if session_key not in self.memory_fallback["session_cache"]:
            self.memory_fallback["session_cache"][session_key] = str(uuid.uuid4())
        
        return self.memory_fallback["session_cache"][session_key]
    
    async def get_conversation_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get conversation analytics for the user"""
        
        history = await self.get_conversation_history(user_id, limit=100)
        
        analytics = {
            "total_conversations": len(history),
            "agents_used": {},
            "success_rate": 0,
            "average_response_time": 0,
            "most_active_day": None,
            "conversation_topics": []
        }
        
        if not history:
            return analytics
        
        successful = 0
        total_response_time = 0
        daily_count = {}
        
        for conv in history:
            # Agent usage
            agent = conv.get("agent_used", "unknown")
            analytics["agents_used"][agent] = analytics["agents_used"].get(agent, 0) + 1
            
            # Success rate
            if conv.get("success", False):
                successful += 1
            
            # Response time
            response_time = conv.get("response_time_ms", 0)
            total_response_time += response_time
            
            # Daily activity
            day = conv.get("timestamp", datetime.utcnow()).strftime("%Y-%m-%d")
            daily_count[day] = daily_count.get(day, 0) + 1
        
        analytics["success_rate"] = (successful / len(history)) * 100 if history else 0
        analytics["average_response_time"] = total_response_time / len(history) if history else 0
        analytics["most_active_day"] = max(daily_count, key=daily_count.get) if daily_count else None
        
        return analytics
    
    async def clear_old_conversations(self, days_old: int = 30):
        """Clean up old conversations"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        if self.connected:
            try:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    self.conversations.delete_many,
                    {"timestamp": {"$lt": cutoff_date}}
                )
                logger.info(f"🗑️ Cleaned up {result.deleted_count} old conversations")
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
    
    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("📁 MongoDB connection closed")

# Global conversation memory instance
conversation_memory = ConversationMemory()