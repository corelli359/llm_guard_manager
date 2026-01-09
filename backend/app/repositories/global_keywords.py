from typing import List
from sqlalchemy import select
from app.repositories.base import BaseRepository
from app.models.db_meta import GlobalKeywords

class GlobalKeywordsRepository(BaseRepository[GlobalKeywords]):
    async def search(self, keyword: str) -> List[GlobalKeywords]:
        result = await self.db.execute(select(self.model).where(self.model.keyword.like(f"%{keyword}%")))
        return result.scalars().all()
