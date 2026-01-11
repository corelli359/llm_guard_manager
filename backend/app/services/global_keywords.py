import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.global_keywords import GlobalKeywordsRepository
from app.schemas.global_keywords import GlobalKeywordsCreate, GlobalKeywordsUpdate
from app.models.db_meta import GlobalKeywords

class GlobalKeywordsService:
    def __init__(self, db: AsyncSession):
        self.repository = GlobalKeywordsRepository(GlobalKeywords, db)

    async def create_keyword(self, keyword_in: GlobalKeywordsCreate) -> GlobalKeywords:
        # Check for duplicates
        existing_keyword = await self.repository.get_by_keyword(keyword_in.keyword)
        if existing_keyword:
            raise ValueError(f"Keyword '{keyword_in.keyword}' already exists.")

        obj_in_data = keyword_in.model_dump()
        obj_in_data['id'] = str(uuid.uuid4())
        return await self.repository.create(obj_in_data)

    async def get_keyword(self, keyword_id: str) -> Optional[GlobalKeywords]:
        return await self.repository.get(keyword_id)

    async def get_all_keywords(
        self, 
        skip: int = 0, 
        limit: int = 100,
        keyword: Optional[str] = None,
        tag_code: Optional[str] = None
    ) -> List[GlobalKeywords]:
        return await self.repository.get_all(skip, limit, keyword, tag_code)

    async def update_keyword(self, keyword_id: str, keyword_in: GlobalKeywordsUpdate) -> GlobalKeywords:
        keyword = await self.repository.get(keyword_id)
        if not keyword:
            raise ValueError("Keyword not found")
        return await self.repository.update(keyword, keyword_in)

    async def delete_keyword(self, keyword_id: str) -> Optional[GlobalKeywords]:
        return await self.repository.delete(keyword_id)
