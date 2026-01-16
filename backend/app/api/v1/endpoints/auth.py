from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.security import create_access_token, verify_password, get_password_hash
from app.core.db import get_db
from app.models.db_meta import User

router = APIRouter()

# Hardcoded user for this task
HARDCODED_USERNAME = "llm_guard"
# Hashed password for "68-8CtBhug"
HARDCODED_HASHED_PASSWORD = "$2b$12$kL2oKnM0Qs5jNa3dT/GDbegCYyG5VpTCrgwgQkq/czEwuFQNfzAY."


@router.post("/access-token", response_model=dict)
async def login_access_token(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user_role = "AUDITOR"
    username = form_data.username

    # 1. Check Hardcoded Admin
    if username == HARDCODED_USERNAME:
        if not verify_password(form_data.password, HARDCODED_HASHED_PASSWORD):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_role = "ADMIN"
    else:
        # 2. Check Database User
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        user = result.scalars().first()
        
        if not user or not verify_password(form_data.password, user.hashed_password):
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
             raise HTTPException(status_code=400, detail="Inactive user")
        user_role = user.role

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            subject=username, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "role": user_role
    }