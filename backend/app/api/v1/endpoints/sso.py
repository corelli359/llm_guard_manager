"""SSO单点登录API端点"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.schemas.sso import (
    SSOLoginRequest,
    SSOLoginResponse,
    SSOUserInfoResponse,
    SSOBatchUsersRequest,
    SSOBatchUsersResponse,
    SSOUserBrief
)
from app.services.sso_service import sso_service, SSOServiceError
from app.api.v1.deps import get_current_user_id
from app.clients.usap_client import usap_client, USAPClientError

router = APIRouter()


@router.post("/login", response_model=SSOLoginResponse)
async def sso_login(
    request: SSOLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    SSO单点登录

    使用USAP颁发的Ticket进行登录，验证成功后返回JWT Token
    """
    try:
        result = await sso_service.login_with_ticket(request.ticket, db)
        return result
    except SSOServiceError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"登录失败: {str(e)}")


@router.get("/user-info", response_model=SSOUserInfoResponse)
async def get_current_user_info(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户完整信息

    从USAP获取用户基本信息，结合本地权限信息返回
    """
    try:
        result = await sso_service.get_user_info(user_id, db)
        if not result:
            raise HTTPException(status_code=404, detail="用户不存在")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户信息失败: {str(e)}")


@router.post("/users/batch", response_model=SSOBatchUsersResponse)
async def get_users_batch(
    request: SSOBatchUsersRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    批量获取用户信息

    从USAP批量获取用户基本信息，用于列表页面显示
    """
    try:
        users, not_found = await usap_client.get_users_batch(request.user_ids)

        return SSOBatchUsersResponse(
            users=[
                SSOUserBrief(
                    user_id=u.user_id,
                    user_name=u.user_name,
                    email=u.email,
                    department=u.department
                )
                for u in users
            ],
            not_found=not_found
        )
    except USAPClientError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户信息失败: {str(e)}")


@router.get("/health")
async def sso_health():
    """
    SSO服务健康检查

    检查USAP服务是否可用
    """
    usap_healthy = await usap_client.health_check()

    return {
        "sso_enabled": True,
        "usap_healthy": usap_healthy
    }
