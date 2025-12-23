"""
LLM service for OpenRouter integration and context management.
"""
from openai import OpenAI
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from uuid import UUID

from ..config import settings
from ..models import Message
from .memory_service import memory_service
from .protocol_service import protocol_service


class LLMService:
    """Service for LLM interactions via OpenRouter."""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.AI_BASE_URL
        )
        self.model = settings.AI_MODEL
        self.temperature = settings.AI_TEMPERATURE
        self.max_tokens = settings.AI_MAX_TOKENS
    
    def count_tokens(self, text: str) -> int:
        """
        Estimate token count using character-based approximation.
        Rough estimate: ~4 characters per token for English text.
        This is sufficient for context management without requiring tiktoken.
        """
        return len(text) // 4
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for Disha health coach."""
        return """You are Disha, India's first AI health coach. You are warm, empathetic, and professional - like a caring friend on WhatsApp who happens to be a health expert.

Your role is to:
- Provide personalized health guidance based on user context and history
- Ask thoughtful clarifying questions to understand their situation better
- Follow medical protocols when applicable for common health issues
- Be conversational, supportive, and natural - NOT clinical or robotic
- Remember user details and reference them naturally in conversation
- Keep responses concise (2-4 sentences typically) like a real chat conversation

IMPORTANT GUIDELINES:
- NEVER provide emergency medical advice - always suggest seeing a doctor for serious/emergency situations
- Be culturally sensitive and aware of Indian context
- Use simple, easy-to-understand language
- Show empathy and emotional support
- Focus on preventive care and healthy lifestyle guidance
- Respect user privacy and confidentiality
- Do not provide any medical advice
- Do not provide outside information except for Dishai's website
- Do not provide any contact information
- Do not write, say or suggest any prescription
- Do not write, say or suggest any medical test
- Do not write, say or talk about AI ,code and outside information 
- Do not write, say or talk about any other health coach or AI health coach
- Never write , share or provide external information except for Dishai's website and related information

Remember: You're a supportive health coach, not a replacement for professional medical care."""
    
    def get_onboarding_prompt(self, user_name: Optional[str] = None) -> str:
        """Get onboarding conversation starter."""
        if user_name:
            return f"Hi {user_name}! 👋 I'm Disha, your personal health coach. I'm here to support you on your health journey. To get started, could you tell me a bit about yourself? What brings you here today?"
        else:
            return "Hi there! 👋 I'm Disha, your personal health coach. I'm excited to support you on your health journey! What's your name?"
    
    def build_context(
        self,
        user_id: UUID,
        user_message: str,
        db: Session
    ) -> List[Dict[str, str]]:
        """
        Build context for LLM call with token management.
        
        Args:
            user_id: User ID
            user_message: Current user message
            db: Database session
            
        Returns:
            List of message dictionaries for OpenAI API
        """
        messages = []
        total_tokens = 0
        max_input_tokens = settings.MAX_INPUT_TOKENS
        
        # 1. System prompt
        system_prompt = self.get_system_prompt()
        system_tokens = self.count_tokens(system_prompt)
        total_tokens += system_tokens
        
        # 2. Get relevant memories
        memories = memory_service.get_relevant_memories(user_id, db, limit=5)
        memory_context = memory_service.format_memories_for_context(memories)
        memory_tokens = self.count_tokens(memory_context)
        total_tokens += memory_tokens
        
        # 3. Match protocols
        matched_protocols = protocol_service.match_protocols(user_message, db)
        protocol_context = protocol_service.format_protocols_for_context(matched_protocols)
        protocol_tokens = self.count_tokens(protocol_context)
        total_tokens += protocol_tokens
        
        # 4. Combine system prompt with context
        full_system_prompt = system_prompt
        if memory_context:
            full_system_prompt += f"\n\n{memory_context}"
        if protocol_context:
            full_system_prompt += f"\n\n{protocol_context}"
        
        messages.append({"role": "system", "content": full_system_prompt})
        
        # 5. Get recent conversation history
        recent_messages = db.query(Message).filter(
            Message.user_id == user_id
        ).order_by(Message.created_at.desc()).limit(
            settings.MAX_CONTEXT_MESSAGES
        ).all()
        
        recent_messages.reverse()  # Chronological order
        
        # Add messages while staying within token budget
        conversation_messages = []
        for msg in recent_messages:
            msg_tokens = self.count_tokens(msg.content)
            if total_tokens + msg_tokens < max_input_tokens - 200:  # Reserve for current message
                conversation_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
                total_tokens += msg_tokens
            else:
                break
        
        messages.extend(conversation_messages)
        
        # 6. Add current message
        current_msg_tokens = self.count_tokens(user_message)
        total_tokens += current_msg_tokens
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def generate_response(
        self,
        user_id: UUID,
        user_message: str,
        db: Session,
        is_onboarding: bool = False
    ) -> str:
        """
        Generate AI response using OpenRouter.
        
        Args:
            user_id: User ID
            user_message: User's message
            db: Database session
            is_onboarding: Whether this is part of onboarding
            
        Returns:
            AI generated response
        """
        try:
            # Build context
            messages = self.build_context(user_id, user_message, db)
            
            # Call OpenRouter API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            
            # Extract response
            ai_message = response.choices[0].message.content
            
            # Check if we should extract memories
            if memory_service.should_extract_memories(user_id, db, interval=settings.MEMORY_EXTRACTION_INTERVAL):
                # Summarize recent conversation for memory extraction
                conversation_text = f"{user_message} {ai_message}"
                memory_service.extract_and_store_memories(user_id, conversation_text, db)
            
            return ai_message
            
        except Exception as e:
            print(f"LLM Error: {e}")
            # Fallback response
            return "I apologize, but I'm having trouble processing your message right now. Could you please try again in a moment?"


# Global LLM service instance
llm_service = LLMService()
