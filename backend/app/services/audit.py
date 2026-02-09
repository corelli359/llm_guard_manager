"""
审计日志服务
负责记录和查询审计日志
"""

import uuid
from typing import Dict, Optional, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request

from app.models.db_meta import AuditLog
from app.repositories.audit_log import AuditLogRepository


class AuditService:
    """审计日志服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = AuditLogRepository(AuditLog, db)

    async def log(
        self,
        user_id: str,
        username: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        scenario_id: Optional[str] = None,
        details: Optional[Dict] = None,
        request: Optional[Request] = None
    ) -> AuditLog:
        """
        记录审计日志

        Args:
            user_id: 用户ID
            username: 用户名
            action: 操作类型（CREATE, UPDATE, DELETE, VIEW, EXPORT）
            resource_type: 资源类型（USER, SCENARIO, KEYWORD, POLICY, etc.）
            resource_id: 资源ID（可选）
            scenario_id: 关联的场景ID（可选）
            details: 操作详情（可选）
            request: FastAPI Request 对象（可选，用于提取 IP 和 User-Agent）

        Returns:
            创建的审计日志对象
        """
        # 提取 IP 地址和 User-Agent
        ip_address = None
        user_agent = None

        if request:
            # 获取真实 IP（考虑代理）
            ip_address = self._get_client_ip(request)
            # 获取 User-Agent
            user_agent = request.headers.get("user-agent")

        # 创建审计日志
        log_data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "username": username,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "scenario_id": scenario_id,
            "details": details,
            "ip_address": ip_address,
            "user_agent": user_agent
        }

        return await self.repository.create(log_data)

    def _get_client_ip(self, request: Request) -> Optional[str]:
        """
        获取客户端真实 IP 地址（考虑代理）

        Args:
            request: FastAPI Request 对象

        Returns:
            IP 地址
        """
        # 尝试从 X-Forwarded-For 头获取（代理情况）
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # X-Forwarded-For 可能包含多个 IP，取第一个
            return forwarded_for.split(",")[0].strip()

        # 尝试从 X-Real-IP 头获取
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()

        # 直接从 client 获取
        if request.client:
            return request.client.host

        return None

    async def log_create(
        self,
        user_id: str,
        username: str,
        resource_type: str,
        resource_id: str,
        scenario_id: Optional[str] = None,
        details: Optional[Dict] = None,
        request: Optional[Request] = None
    ) -> AuditLog:
        """
        记录创建操作

        Args:
            user_id: 用户ID
            username: 用户名
            resource_type: 资源类型
            resource_id: 资源ID
            scenario_id: 场景ID（可选）
            details: 操作详情（可选）
            request: Request 对象（可选）

        Returns:
            审计日志对象
        """
        return await self.log(
            user_id=user_id,
            username=username,
            action="CREATE",
            resource_type=resource_type,
            resource_id=resource_id,
            scenario_id=scenario_id,
            details=details,
            request=request
        )

    async def log_update(
        self,
        user_id: str,
        username: str,
        resource_type: str,
        resource_id: str,
        scenario_id: Optional[str] = None,
        details: Optional[Dict] = None,
        request: Optional[Request] = None
    ) -> AuditLog:
        """
        记录更新操作

        Args:
            user_id: 用户ID
            username: 用户名
            resource_type: 资源类型
            resource_id: 资源ID
            scenario_id: 场景ID（可选）
            details: 操作详情（可选）
            request: Request 对象（可选）

        Returns:
            审计日志对象
        """
        return await self.log(
            user_id=user_id,
            username=username,
            action="UPDATE",
            resource_type=resource_type,
            resource_id=resource_id,
            scenario_id=scenario_id,
            details=details,
            request=request
        )

    async def log_delete(
        self,
        user_id: str,
        username: str,
        resource_type: str,
        resource_id: str,
        scenario_id: Optional[str] = None,
        details: Optional[Dict] = None,
        request: Optional[Request] = None
    ) -> AuditLog:
        """
        记录删除操作

        Args:
            user_id: 用户ID
            username: 用户名
            resource_type: 资源类型
            resource_id: 资源ID
            scenario_id: 场景ID（可选）
            details: 操作详情（可选）
            request: Request 对象（可选）

        Returns:
            审计日志对象
        """
        return await self.log(
            user_id=user_id,
            username=username,
            action="DELETE",
            resource_type=resource_type,
            resource_id=resource_id,
            scenario_id=scenario_id,
            details=details,
            request=request
        )

    async def log_view(
        self,
        user_id: str,
        username: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        scenario_id: Optional[str] = None,
        details: Optional[Dict] = None,
        request: Optional[Request] = None
    ) -> AuditLog:
        """
        记录查看操作

        Args:
            user_id: 用户ID
            username: 用户名
            resource_type: 资源类型
            resource_id: 资源ID（可选）
            scenario_id: 场景ID（可选）
            details: 操作详情（可选）
            request: Request 对象（可选）

        Returns:
            审计日志对象
        """
        return await self.log(
            user_id=user_id,
            username=username,
            action="VIEW",
            resource_type=resource_type,
            resource_id=resource_id,
            scenario_id=scenario_id,
            details=details,
            request=request
        )

    async def log_export(
        self,
        user_id: str,
        username: str,
        resource_type: str,
        scenario_id: Optional[str] = None,
        details: Optional[Dict] = None,
        request: Optional[Request] = None
    ) -> AuditLog:
        """
        记录导出操作

        Args:
            user_id: 用户ID
            username: 用户名
            resource_type: 资源类型
            scenario_id: 场景ID（可选）
            details: 操作详情（可选）
            request: Request 对象（可选）

        Returns:
            审计日志对象
        """
        return await self.log(
            user_id=user_id,
            username=username,
            action="EXPORT",
            resource_type=resource_type,
            scenario_id=scenario_id,
            details=details,
            request=request
        )
