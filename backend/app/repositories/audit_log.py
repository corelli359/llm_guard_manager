"""
审计日志 Repository
负责审计日志的数据访问和查询
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_meta import AuditLog
from app.repositories.base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    """审计日志 Repository"""

    async def search_logs(
        self,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        scenario_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        """
        根据条件搜索审计日志

        Args:
            user_id: 用户ID
            username: 用户名
            action: 操作类型
            resource_type: 资源类型
            scenario_id: 场景ID
            start_date: 开始日期
            end_date: 结束日期
            skip: 跳过记录数
            limit: 返回记录数

        Returns:
            审计日志列表
        """
        query = select(self.model)

        # 构建过滤条件
        conditions = []

        if user_id:
            conditions.append(self.model.user_id == user_id)

        if username:
            conditions.append(self.model.username.like(f"%{username}%"))

        if action:
            conditions.append(self.model.action == action)

        if resource_type:
            conditions.append(self.model.resource_type == resource_type)

        if scenario_id:
            conditions.append(self.model.scenario_id == scenario_id)

        if start_date:
            conditions.append(self.model.created_at >= start_date)

        if end_date:
            conditions.append(self.model.created_at <= end_date)

        # 应用过滤条件
        if conditions:
            query = query.where(and_(*conditions))

        # 按时间倒序排列
        query = query.order_by(self.model.created_at.desc())

        # 分页
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_user_logs(
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[AuditLog]:
        """
        获取特定用户的审计日志

        Args:
            user_id: 用户ID
            skip: 跳过记录数
            limit: 返回记录数

        Returns:
            审计日志列表
        """
        query = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_scenario_logs(
        self, scenario_id: str, skip: int = 0, limit: int = 100
    ) -> List[AuditLog]:
        """
        获取特定场景的审计日志

        Args:
            scenario_id: 场景ID
            skip: 跳过记录数
            limit: 返回记录数

        Returns:
            审计日志列表
        """
        query = (
            select(self.model)
            .where(self.model.scenario_id == scenario_id)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_recent_logs(self, limit: int = 100) -> List[AuditLog]:
        """
        获取最近的审计日志

        Args:
            limit: 返回记录数

        Returns:
            审计日志列表
        """
        query = (
            select(self.model)
            .order_by(self.model.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_logs(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        scenario_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        """
        统计符合条件的审计日志数量

        Args:
            user_id: 用户ID
            action: 操作类型
            resource_type: 资源类型
            scenario_id: 场景ID
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            日志数量
        """
        from sqlalchemy import func as sql_func

        query = select(sql_func.count(self.model.id))

        # 构建过滤条件
        conditions = []

        if user_id:
            conditions.append(self.model.user_id == user_id)

        if action:
            conditions.append(self.model.action == action)

        if resource_type:
            conditions.append(self.model.resource_type == resource_type)

        if scenario_id:
            conditions.append(self.model.scenario_id == scenario_id)

        if start_date:
            conditions.append(self.model.created_at >= start_date)

        if end_date:
            conditions.append(self.model.created_at <= end_date)

        # 应用过滤条件
        if conditions:
            query = query.where(and_(*conditions))

        result = await self.db.execute(query)
        return result.scalar() or 0
