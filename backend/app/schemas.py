"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# ==================== User Schemas ====================

class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    user_metadata: Dict[str, Any] = Field(default_factory=dict)


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Message Schemas ====================

class MessageBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)


class MessageCreate(BaseModel):
    user_id: UUID
    content: str = Field(..., min_length=1, max_length=5000)
    is_onboarding: bool = False
    
    @validator('content')
    def content_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Message content cannot be empty or whitespace')
        return v.strip()


class MessageResponse(BaseModel):
    id: UUID
    user_id: UUID
    role: str
    content: str
    created_at: datetime
    is_onboarding: bool
    
    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    user_message: MessageResponse
    ai_response: MessageResponse


# ==================== Message History Schemas ====================

class MessageHistoryRequest(BaseModel):
    user_id: UUID
    before: Optional[UUID] = None  # Cursor for pagination
    limit: int = Field(default=50, ge=1, le=100)


class MessageHistoryResponse(BaseModel):
    messages: List[MessageResponse]
    has_more: bool
    next_cursor: Optional[UUID] = None


# ==================== Memory Schemas ====================

class MemoryBase(BaseModel):
    content: str
    category: str
    importance_score: float = Field(default=0.5, ge=0.0, le=1.0)


class MemoryCreate(MemoryBase):
    user_id: UUID


class MemoryResponse(MemoryBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Protocol Schemas ====================

class ProtocolBase(BaseModel):
    name: str
    description: str
    instructions: Dict[str, Any]
    keywords: List[str]


class ProtocolCreate(ProtocolBase):
    pass


class ProtocolResponse(ProtocolBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Onboarding Schemas ====================

class OnboardingRequest(BaseModel):
    user_id: UUID
    message: Optional[str] = None


class OnboardingResponse(BaseModel):
    message: str
    onboarding_complete: bool
    user_id: UUID


# ==================== Health Check ====================

class HealthCheckResponse(BaseModel):
    status: str
    app_name: str
    timestamp: datetime
