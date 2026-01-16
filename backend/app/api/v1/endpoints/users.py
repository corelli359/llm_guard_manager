from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.db import get_db
from app.api.v1.deps import get_current_user
from app.models.db_meta import User
from app.core.security import get_password_hash
from pydantic import BaseModel
from datetime import datetime
import secrets
import uuid

router = APIRouter()

class UserCreate(BaseModel):
    username: str

class UserResponse(BaseModel):
    username: str
    password: str # Only returned once on creation

class UserListResponse(BaseModel):
    id: str
    username: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserStatusUpdate(BaseModel):
    is_active: bool

@router.post("/", response_model=UserResponse)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    # Only "llm_guard" (Hardcoded Admin) can create users for now
    if current_user != "llm_guard":
        raise HTTPException(status_code=403, detail="Not authorized")

    # Check existence
    stmt = select(User).where(User.username == user_in.username)
    result = await db.execute(stmt)
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="User already exists")

    # Generate random password
    raw_password = secrets.token_urlsafe(10)
    hashed = get_password_hash(raw_password)

    new_user = User(
        id=str(uuid.uuid4()),
        username=user_in.username,
        hashed_password=hashed,
        role="AUDITOR",
        is_active=True
    )
    db.add(new_user)
    await db.commit()
    
    return {"username": user_in.username, "password": raw_password}

@router.get("/", response_model=List[UserListResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    if current_user != "llm_guard":
        raise HTTPException(status_code=403, detail="Not authorized")
        
    stmt = select(User).order_by(User.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.patch("/{user_id}/status")
async def toggle_user_status(
    user_id: str,
    status_in: UserStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    if current_user != "llm_guard":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.is_active = status_in.is_active
    await db.commit()
    return {"message": "Status updated"}

@router.post("/{user_id}/reset-password", response_model=UserResponse)
async def reset_password(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    if current_user != "llm_guard":
        raise HTTPException(status_code=403, detail="Not authorized")

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    raw_password = secrets.token_urlsafe(10)
    user.hashed_password = get_password_hash(raw_password)
    await db.commit()
    
    return {"username": user.username, "password": raw_password}

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    if current_user != "llm_guard":
        raise HTTPException(status_code=403, detail="Not authorized")
        
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if user:
        await db.delete(user)
        await db.commit()
    return {"message": "User deleted"}