from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_db
from app.models.db_meta import User

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"/api/v1/login/access-token"
)

class TokenData(BaseModel):
    username: str | None = None
    user_id: str | None = None  # SSO用户使用user_id


async def get_current_user_id(token: str = Depends(reusable_oauth2)) -> str:
    """
    获取当前用户ID（支持SSO）

    从JWT Token中提取user_id（SSO）或username（传统登录）

    Args:
        token: JWT Token

    Returns:
        用户ID（user_id或username）

    Raises:
        HTTPException: 401 如果 Token 无效
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        # sub字段可能是user_id（SSO）或username（传统登录）
        sub: str = payload.get("sub")
        if sub is None:
            raise credentials_exception
        return sub
    except JWTError:
        raise credentials_exception


async def get_current_user(token: str = Depends(reusable_oauth2)) -> str:
    """
    获取当前用户名（保留向后兼容）

    Args:
        token: JWT Token

    Returns:
        用户名

    Raises:
        HTTPException: 401 如果 Token 无效
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    if token_data.username is None:
        raise credentials_exception
    return token_data.username


async def get_current_user_full(
    token: str = Depends(reusable_oauth2),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    获取完整的当前用户对象（支持SSO和传统登录）

    Args:
        token: JWT Token
        db: 数据库会话

    Returns:
        User 对象

    Raises:
        HTTPException: 401 如果 Token 无效或用户不存在
        HTTPException: 403 如果用户被禁用
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        sub: str = payload.get("sub")
        if sub is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 查询数据库获取完整用户信息（支持user_id和username两种方式）
    query = select(User).where(
        or_(User.user_id == sub, User.username == sub)
    )
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    return user


def require_role(allowed_roles: List[str]):
    """
    角色检查依赖工厂

    Args:
        allowed_roles: 允许的角色列表

    Returns:
        依赖函数

    Example:
        @router.post("/")
        async def create_user(
            current_user: User = Depends(require_role(["SYSTEM_ADMIN"]))
        ):
            ...
    """
    async def role_checker(
        current_user: User = Depends(get_current_user_full)
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {', '.join(allowed_roles)}"
            )
        return current_user

    return role_checker


def require_scenario_permission(permission: str):
    """
    场景权限检查依赖工厂

    Args:
        permission: 需要的权限名称（scenario_basic_info, scenario_keywords, etc.）

    Returns:
        依赖函数

    Example:
        @router.post("/{scenario_id}/keywords")
        async def create_keyword(
            scenario_id: str,
            current_user: User = Depends(require_scenario_permission("scenario_keywords"))
        ):
            ...
    """
    async def permission_checker(
        scenario_id: str,
        current_user: User = Depends(get_current_user_full),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        from app.services.permission import PermissionService

        # SYSTEM_ADMIN 有所有权限
        if current_user.role == "SYSTEM_ADMIN":
            return current_user

        # 其他角色需要检查权限
        perm_service = PermissionService(db)
        has_perm = await perm_service.check_scenario_permission(
            current_user.id, scenario_id, permission
        )

        if not has_perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission: {permission} for scenario: {scenario_id}"
            )

        return current_user

    return permission_checker
