from typing import List, Optional
from sqlalchemy import select
from app.repositories.base import BaseRepository
from app.models.db_meta import GlobalKeywords

class GlobalKeywordsRepository(BaseRepository[GlobalKeywords]):
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        keyword: Optional[str] = None, 
        tag_code: Optional[str] = None
    ) -> List[GlobalKeywords]:
        query = select(self.model)
        
        if keyword:
            query = query.where(self.model.keyword.like(f"%{keyword}%"))
        
        if tag_code:
            query = query.where(self.model.tag_code == tag_code)
            
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_keyword(self, keyword_text: str) -> Optional[GlobalKeywords]:
        query = select(self.model).where(self.model.keyword == keyword_text)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def search(self, keyword: str) -> List[GlobalKeywords]:
        result = await self.db.execute(select(self.model).where(self.model.keyword.like(f"%{keyword}%")))
        return result.scalars().all()
