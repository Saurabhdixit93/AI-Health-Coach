"""
SQLAlchemy database models for the Disha AI Health Coach.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Boolean, Float, Integer, DateTime, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    """User model representing a health coach user."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    user_metadata = Column(JSONB, default=dict)  # Stores age, health conditions, preferences, etc.
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")
    memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, name={self.name})>"


class Message(Base):
    """Message model for chat history."""
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    is_onboarding = Column(Boolean, default=False)
    token_count = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="messages")
    
    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role}, user_id={self.user_id})>"


class Memory(Base):
    """Long-term memory storage for user context."""
    __tablename__ = "memories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)  # e.g., 'demographics', 'health_condition', 'medication'
    importance_score = Column(Float, default=0.5)  # 0.0 to 1.0
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="memories")
    
    def __repr__(self):
        return f"<Memory(id={self.id}, category={self.category}, user_id={self.user_id})>"


class Protocol(Base):
    """Medical and operational protocols."""
    __tablename__ = "protocols"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    instructions = Column(JSONB, nullable=False)  # Structured protocol steps
    keywords = Column(ARRAY(String), nullable=False)  # Keywords for matching
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    def __repr__(self):
        return f"<Protocol(id={self.id}, name={self.name})>"
