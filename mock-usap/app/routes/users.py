from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from ..services import user_service

router = APIRouter()


class BatchUsersRequest(BaseModel):
    user_ids: List[str]


@router.get("/{user_id}")
async def get_user(user_id: str):
    """获取单个用户信息"""
    user = user_service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return {
        "user_id": user["user_id"],
        "user_name": user["user_name"],
        "email": user["email"],
        "department": user["department"],
        "phone": user["phone"],
        "status": user["status"]
    }


@router.post("/batch")
async def get_users_batch(request: BatchUsersRequest):
    """批量获取用户信息"""
    found, not_found = user_service.get_users_by_ids(request.user_ids)

    users = [
        {
            "user_id": user["user_id"],
            "user_name": user["user_name"],
            "email": user["email"],
            "department": user["department"]
        }
        for user in found
    ]

    return {
        "users": users,
        "not_found": not_found
    }
