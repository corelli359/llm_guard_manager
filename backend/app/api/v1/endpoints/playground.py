from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.api.v1.deps import get_current_user
from app.schemas.playground import PlaygroundInputRequest, PlaygroundHistorySchema
from app.services.playground import PlaygroundService

router = APIRouter()

@router.post("/input", response_model=Any)
async def playground_input(
    payload: PlaygroundInputRequest,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
) -> Any:
    service = PlaygroundService(db)
    try:
        result = await service.run_input_check(payload)
        return result
    except Exception as e:
        # Check if it's an HTTPException already
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Error processing playground request: {str(e)}"
        )

@router.get("/history", response_model=List[PlaygroundHistorySchema])
async def get_playground_history(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    playground_type: Optional[str] = None,
    app_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
) -> Any:
    service = PlaygroundService(db)
    return await service.get_history(page, size, playground_type, app_id)