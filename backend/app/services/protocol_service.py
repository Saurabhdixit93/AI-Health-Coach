"""
Protocol matching service for medical and operational protocols.
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from ..models import Protocol
from .cache_service import cache_service


class ProtocolService:
    """Service for matching and retrieving relevant protocols."""
    
    @staticmethod
    def get_all_protocols(db: Session) -> List[Protocol]:
        """Get all protocols from database."""
        return db.query(Protocol).all()
    
    @staticmethod
    def get_protocols_with_cache(db: Session) -> List[Protocol]:
        """Get protocols with caching for better performance."""
        # Try cache first
        cached = cache_service.get_cached_protocols()
        if cached:
            # Convert cached data back to protocol objects
            return [Protocol(**p) for p in cached]
        
        # Fetch from database
        protocols = ProtocolService.get_all_protocols(db)
        
        # Cache for future use
        cache_data = [
            {
                "id": str(p.id),
                "name": p.name,
                "description": p.description,
                "instructions": p.instructions,
                "keywords": p.keywords
            }
            for p in protocols
        ]
        cache_service.cache_protocols(cache_data)
        
        return protocols
    
    @staticmethod
    def match_protocols(message: str, db: Session) -> List[Protocol]:
        """
        Match protocols based on keywords in the message.
        
        Args:
            message: User's message content
            db: Database session
            
        Returns:
            List of matched protocols
        """
        protocols = ProtocolService.get_protocols_with_cache(db)
        matched = []
        
        message_lower = message.lower()
        
        for protocol in protocols:
            # Check if any keyword matches
            for keyword in protocol.keywords:
                if keyword.lower() in message_lower:
                    matched.append(protocol)
                    break  # Don't add the same protocol multiple times
        
        return matched
    
    @staticmethod
    def format_protocols_for_context(protocols: List[Protocol]) -> str:
        """
        Format matched protocols for inclusion in LLM context.
        
        Args:
            protocols: List of matched protocols
            
        Returns:
            Formatted string for LLM context
        """
        if not protocols:
            return ""
        
        formatted = "\n[PROTOCOLS]\n"
        for protocol in protocols:
            formatted += f"\n**{protocol.name}**\n"
            formatted += f"{protocol.description}\n"
            
            if isinstance(protocol.instructions, dict):
                if "steps" in protocol.instructions:
                    formatted += "Steps:\n"
                    for i, step in enumerate(protocol.instructions["steps"], 1):
                        formatted += f"{i}. {step}\n"
                
                if "warnings" in protocol.instructions:
                    formatted += f"\nWarnings: {', '.join(protocol.instructions['warnings'])}\n"
            
            formatted += "\n"
        
        return formatted


# Global protocol service instance
protocol_service = ProtocolService()
