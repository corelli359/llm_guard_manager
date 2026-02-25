from typing import List, Optional, Tuple
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.db_meta import EvalTaskResult


class EvalTaskResultRepository(BaseRepository[EvalTaskResult]):
    def __init__(self, db: AsyncSession):
        super().__init__(EvalTaskResult, db)

    async def get_by_task(
        self, task_id: str, skip: int = 0, limit: int = 50,
        guardrail_result: Optional[str] = None, is_correct: Optional[bool] = None,
    ) -> Tuple[List[EvalTaskResult], int]:
        query = select(EvalTaskResult).where(EvalTaskResult.task_id == task_id)
        count_query = select(func.count()).select_from(EvalTaskResult).where(EvalTaskResult.task_id == task_id)

        if guardrail_result:
            query = query.where(EvalTaskResult.guardrail_result == guardrail_result)
            count_query = count_query.where(EvalTaskResult.guardrail_result == guardrail_result)
        if is_correct is not None:
            query = query.where(EvalTaskResult.is_correct == is_correct)
            count_query = count_query.where(EvalTaskResult.is_correct == is_correct)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(EvalTaskResult.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all(), total

    async def get_all_by_task(self, task_id: str) -> List[EvalTaskResult]:
        query = select(EvalTaskResult).where(EvalTaskResult.task_id == task_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def delete_by_task(self, task_id: str):
        stmt = delete(EvalTaskResult).where(EvalTaskResult.task_id == task_id)
        await self.db.execute(stmt)
        await self.db.commit()
