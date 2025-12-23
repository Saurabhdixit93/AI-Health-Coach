"""
Chat routes for message handling and conversation management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from datetime import datetime

from ..database import get_db
from ..models import User, Message
from ..schemas import (
    MessageCreate,
    MessageResponse,
    ChatResponse,
    MessageHistoryResponse,
    OnboardingRequest,
    OnboardingResponse
)
from ..services.llm_service import llm_service
from ..services.cache_service import cache_service

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/messages", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    message_data: MessageCreate,
    db: Session = Depends(get_db)
):
    """
    Send a message and receive AI response.
    
    This endpoint:
    1. Validates and stores user message
    2. Sets typing indicator
    3. Generates AI response using LLM service
    4. Stores AI response
    5. Returns both messages
    """
    # Verify user exists
    user = db.query(User).filter(User.id == message_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {message_data.user_id} not found"
        )
    
    # Create and store user message
    user_message = Message(
        user_id=message_data.user_id,
        role="user",
        content=message_data.content,
        is_onboarding=message_data.is_onboarding,
        token_count=llm_service.count_tokens(message_data.content)
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)
    
    # Set typing indicator
    cache_service.set_typing_indicator(str(message_data.user_id), True)
    
    try:
        # Generate AI response
        ai_content = llm_service.generate_response(
            user_id=message_data.user_id,
            user_message=message_data.content,
            db=db,
            is_onboarding=message_data.is_onboarding
        )
        
        # Create and store AI message
        ai_message = Message(
            user_id=message_data.user_id,
            role="assistant",
            content=ai_content,
            is_onboarding=message_data.is_onboarding,
            token_count=llm_service.count_tokens(ai_content)
        )
        db.add(ai_message)
        db.commit()
        db.refresh(ai_message)
        
        # Clear typing indicator
        cache_service.set_typing_indicator(str(message_data.user_id), False)
        
        return ChatResponse(
            user_message=MessageResponse.from_orm(user_message),
            ai_response=MessageResponse.from_orm(ai_message)
        )
        
    except Exception as e:
        # Clear typing indicator on error
        cache_service.set_typing_indicator(str(message_data.user_id), False)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating response: {str(e)}"
        )


@router.get("/messages", response_model=MessageHistoryResponse)
async def get_messages(
    user_id: UUID,
    before: Optional[UUID] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get paginated message history for a user.
    
    Implements cursor-based pagination for efficient infinite scroll.
    
    Args:
        user_id: User ID
        before: Message ID cursor (get messages before this ID)
        limit: Number of messages to return (max 100)
        
    Returns:
        Paginated message history
    """
    # Validate limit
    if limit > 100:
        limit = 100
    
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Build query
    query = db.query(Message).filter(Message.user_id == user_id)
    
    # Apply cursor if provided
    if before:
        cursor_message = db.query(Message).filter(Message.id == before).first()
        if cursor_message:
            query = query.filter(Message.created_at < cursor_message.created_at)
    
    # Order by most recent first and limit
    messages = query.order_by(Message.created_at.desc()).limit(limit + 1).all()
    
    # Check if there are more messages
    has_more = len(messages) > limit
    if has_more:
        messages = messages[:limit]
    
    # Determine next cursor
    next_cursor = messages[-1].id if messages and has_more else None
    
    # Reverse to chronological order for display
    messages.reverse()
    
    return MessageHistoryResponse(
        messages=[MessageResponse.from_orm(msg) for msg in messages],
        has_more=has_more,
        next_cursor=next_cursor
    )


@router.post("/onboarding", response_model=OnboardingResponse)
async def start_onboarding(
    request: OnboardingRequest,
    db: Session = Depends(get_db)
):
    """
    Start or continue onboarding conversation.
    
    This endpoint initializes the conversation with an onboarding flow
    to gather user information.
    """
    # Get or create user
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {request.user_id} not found"
        )
    
    # Check if onboarding is already complete
    onboarding_messages = db.query(Message).filter(
        Message.user_id == request.user_id,
        Message.is_onboarding == True
    ).count()
    
    onboarding_complete = onboarding_messages >= 10  # After ~5 exchanges
    
    if request.message:
        # User provided a response, generate next onboarding question
        ai_response = llm_service.generate_response(
            user_id=request.user_id,
            user_message=request.message,
            db=db,
            is_onboarding=True
        )
    else:
        # Initial onboarding message
        ai_response = llm_service.get_onboarding_prompt(user.name)
    
    return OnboardingResponse(
        message=ai_response,
        onboarding_complete=onboarding_complete,
        user_id=request.user_id
    )


@router.get("/typing/{user_id}")
async def get_typing_status(user_id: UUID):
    """
    Get typing indicator status for a user.
    
    Returns whether the AI is currently generating a response.
    """
    is_typing = cache_service.get_typing_indicator(str(user_id))
    return {"is_typing": is_typing, "user_id": str(user_id)}
