"""
Memory service for extracting and retrieving long-term user memories.
"""
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from ..models import Memory, Message
from ..schemas import MemoryCreate


class MemoryService:
    """Service for managing user's long-term memories."""
    
    @staticmethod
    def should_extract_memories(user_id: UUID, db: Session, interval: int = 5) -> bool:
        """
        Check if we should extract memories based on message count.
        
        Args:
            user_id: User ID
            db: Database session
            interval: Extract memories every N messages
            
        Returns:
            True if memories should be extracted
        """
        message_count = db.query(Message).filter(
            Message.user_id == user_id,
            Message.role == "user"
        ).count()
        
        return message_count > 0 and message_count % interval == 0
    
    @staticmethod
    def extract_and_store_memories(
        user_id: UUID,
        conversation_summary: str,
        db: Session
    ) -> List[Memory]:
        """
        Extract memories from conversation summary and store them.
        
        In a production system, this would use an LLM to extract structured
        information. For this implementation, we'll use simple pattern matching.
        
        Args:
            user_id: User ID
            conversation_summary: Summary of recent conversation
            db: Database session
            
        Returns:
            List of created memories
        """
        memories = []
        summary_lower = conversation_summary.lower()
        
        # Simple extraction patterns (in production, use LLM)
        patterns = {
            "demographics": ["age", "years old", "gender", "location"],
            "health_condition": ["diagnosed", "suffer from", "condition", "disease", "allergy", "allergic"],
            "medication": ["taking", "prescribed", "medicine", "medication", "drug"],
            "lifestyle": ["exercise", "diet", "sleep", "work", "job"],
            "symptoms": ["pain", "ache", "fever", "nausea", "headache", "cough"]
        }
        
        for category, keywords in patterns.items():
            for keyword in keywords:
                if keyword in summary_lower:
                    # Extract sentence containing the keyword
                    sentences = conversation_summary.split('.')
                    for sentence in sentences:
                        if keyword in sentence.lower():
                            memory = Memory(
                                user_id=user_id,
                                content=sentence.strip(),
                                category=category,
                                importance_score=0.7  # Default importance
                            )
                            db.add(memory)
                            memories.append(memory)
                            break
                    break
        
        if memories:
            db.commit()
        
        return memories
    
    @staticmethod
    def get_relevant_memories(
        user_id: UUID,
        db: Session,
        limit: int = 5
    ) -> List[Memory]:
        """
        Get most relevant memories for a user.
        
        Args:
            user_id: User ID
            db: Database session
            limit: Maximum number of memories to return
            
        Returns:
            List of relevant memories
        """
        return db.query(Memory).filter(
            Memory.user_id == user_id
        ).order_by(
            Memory.importance_score.desc(),
            Memory.created_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def format_memories_for_context(memories: List[Memory]) -> str:
        """
        Format memories for inclusion in LLM context.
        
        Args:
            memories: List of memory objects
            
        Returns:
            Formatted string for LLM context
        """
        if not memories:
            return ""
        
        # Group by category
        by_category = {}
        for memory in memories:
            if memory.category not in by_category:
                by_category[memory.category] = []
            by_category[memory.category].append(memory.content)
        
        formatted = "\n[LONG-TERM MEMORIES]\n"
        for category, contents in by_category.items():
            formatted += f"{category.replace('_', ' ').title()}:\n"
            for content in contents:
                formatted += f"- {content}\n"
        
        return formatted


# Global memory service instance
memory_service = MemoryService()
