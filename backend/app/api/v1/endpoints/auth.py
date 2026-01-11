from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
from app.core.security import create_access_token, verify_password, get_password_hash

router = APIRouter()

# Hardcoded user for this task
HARDCODED_USERNAME = "llm_guard"
# Hashed password for "68-8CtBhug"
HARDCODED_HASHED_PASSWORD = "$2b$12$kL2oKnM0Qs5jNa3dT/GDbegCYyG5VpTCrgwgQkq/czEwuFQNfzAY."


@router.post("/access-token", response_model=dict)
async def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    if form_data.username != HARDCODED_USERNAME or \
       not verify_password(form_data.password, HARDCODED_HASHED_PASSWORD):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            subject=form_data.username, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

