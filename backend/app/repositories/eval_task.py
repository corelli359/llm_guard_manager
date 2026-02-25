from typing import List, Optional, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.db_meta import EvalTask


class EvalTaskRepository(BaseRepository[EvalTask]):
    def __init__(self, db: AsyncSession):
        super().__init__(EvalTask, db)

    async def get_filtered(
        self, skip: int = 0, limit: int = 20,
        status: Optional[str] = None, app_id: Optional[str] = None,
    ) -> Tuple[List[EvalTask], int]:
        query = select(EvalTask)
        count_query = select(func.count()).select_from(EvalTask)

        if status:
            query = query.where(EvalTask.status == status)
            count_query = count_query.where(EvalTask.status == status)
        if app_id:
            query = query.where(EvalTask.app_id == app_id)
            count_query = count_query.where(EvalTask.app_id == app_id)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(EvalTask.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all(), total
