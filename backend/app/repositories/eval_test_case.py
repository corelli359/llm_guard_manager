from typing import List, Optional, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.db_meta import EvalTestCase


class EvalTestCaseRepository(BaseRepository[EvalTestCase]):
    def __init__(self, db: AsyncSession):
        super().__init__(EvalTestCase, db)

    async def get_filtered(
        self, skip: int = 0, limit: int = 50,
        keyword: Optional[str] = None, tag_code: Optional[str] = None,
        expected_result: Optional[str] = None,
    ) -> Tuple[List[EvalTestCase], int]:
        query = select(EvalTestCase).where(EvalTestCase.is_active == True)
        count_query = select(func.count()).select_from(EvalTestCase).where(EvalTestCase.is_active == True)

        if keyword:
            query = query.where(EvalTestCase.content.contains(keyword))
            count_query = count_query.where(EvalTestCase.content.contains(keyword))
        if tag_code:
            query = query.where(EvalTestCase.tag_codes.contains(tag_code))
            count_query = count_query.where(EvalTestCase.tag_codes.contains(tag_code))
        if expected_result:
            query = query.where(EvalTestCase.expected_result == expected_result)
            count_query = count_query.where(EvalTestCase.expected_result == expected_result)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(EvalTestCase.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all(), total

    async def get_cases_by_filter(
        self, tag_codes: Optional[List[str]] = None, expected_result: Optional[str] = None
    ) -> List[EvalTestCase]:
        query = select(EvalTestCase).where(EvalTestCase.is_active == True)
        if expected_result:
            query = query.where(EvalTestCase.expected_result == expected_result)
        result = await self.db.execute(query)
        cases = result.scalars().all()
        if tag_codes:
            cases = [c for c in cases if c.tag_codes and any(t in c.tag_codes for t in tag_codes)]
        return cases

    async def count_by_filter(
        self, tag_codes: Optional[List[str]] = None, expected_result: Optional[str] = None
    ) -> int:
        cases = await self.get_cases_by_filter(tag_codes, expected_result)
        return len(cases)
