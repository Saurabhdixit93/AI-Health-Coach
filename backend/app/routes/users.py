"""
User management routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserResponse

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Create a new user."""
    user = User(
        name=user_data.name,
        user_metadata=user_data.user_metadata
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse.from_orm(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Get user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return UserResponse.from_orm(user)
