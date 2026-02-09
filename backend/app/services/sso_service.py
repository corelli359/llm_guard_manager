"""SSO服务 - 处理单点登录逻辑"""
import uuid
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.clients.usap_client import usap_client, TicketValidationResult, UserInfo
from app.models.db_meta import User
from app.schemas.sso import SSOLoginResponse, SSOUserInfoResponse


class SSOServiceError(Exception):
    """SSO服务错误"""
    pass


class SSOService:
    """SSO单点登录服务"""

    async def login_with_ticket(self, ticket: str, db: AsyncSession) -> SSOLoginResponse:
        """
        使用Ticket登录

        流程:
        1. 验证Ticket
        2. 获取UserID
        3. 同步/创建本地用户
        4. 查询用户权限
        5. 生成JWT Token
        """
        # 1. 验证Ticket
        validation_result = await usap_client.validate_ticket(ticket)

        if not validation_result.valid:
            raise SSOServiceError(validation_result.error or "Ticket验证失败")

        # 2. 获取UserID
        user_id = validation_result.user_id
        if not user_id:
            raise SSOServiceError("无法获取用户ID")

        # 3. 同步/创建本地用户
        user = await self._sync_user_from_usap(user_id, validation_result, db)

        # 4. 生成JWT Token
        access_token = self._create_access_token(user_id=user.user_id, role=user.role)

        return SSOLoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_id=user.user_id,
            role=user.role
        )

    async def _sync_user_from_usap(
        self,
        user_id: str,
        validation_result: TicketValidationResult,
        db: AsyncSession
    ) -> User:
        """
        从USAP同步用户信息

        策略:
        1. 查询本地是否存在该用户
        2. 如果不存在，创建新用户（默认角色: ANNOTATOR）
        3. 如果存在，更新最后登录时间
        """
        # 查询本地用户
        query = select(User).where(User.user_id == user_id)
        result = await db.execute(query)
        user = result.scalars().first()

        if not user:
            # 首次登录，创建用户
            user = User(
                id=str(uuid.uuid4()),
                user_id=user_id,
                username=user_id,  # 兼容V1，使用user_id作为username
                hashed_password="",  # SSO用户不需要密码
                display_name=validation_result.user_name,
                role="ANNOTATOR",  # 默认角色
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        else:
            # 更新最后登录时间
            user.updated_at = datetime.utcnow()
            if validation_result.user_name:
                user.display_name = validation_result.user_name
            await db.commit()

        return user

    def _create_access_token(self, user_id: str, role: str) -> str:
        """生成JWT Access Token"""
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        payload = {
            "exp": expire,
            "sub": user_id,
            "role": role
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return token

    async def get_user_info(self, user_id: str, db: AsyncSession) -> Optional[SSOUserInfoResponse]:
        """获取用户完整信息"""
        # 查询本地用户
        query = select(User).where(User.user_id == user_id)
        result = await db.execute(query)
        user = result.scalars().first()

        if not user:
            return None

        # 从USAP获取用户信息
        usap_user = await usap_client.get_user_info(user_id)

        return SSOUserInfoResponse(
            user_id=user.user_id,
            user_name=usap_user.user_name if usap_user else user.display_name or user_id,
            email=usap_user.email if usap_user else None,
            department=usap_user.department if usap_user else None,
            phone=usap_user.phone if usap_user else None,
            role=user.role,
            scenarios=[]  # TODO: 查询用户场景权限
        )


# 单例
sso_service = SSOService()
