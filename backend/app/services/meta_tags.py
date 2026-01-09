import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.meta_tags import MetaTagsRepository
from app.schemas.meta_tags import MetaTagsCreate, MetaTagsUpdate
from app.models.db_meta import MetaTags

class MetaTagsService:
    def __init__(self, db: AsyncSession):
        self.repository = MetaTagsRepository(MetaTags, db)

    async def create_tag(self, tag_in: MetaTagsCreate) -> MetaTags:
        # Check if exists by code
        existing = await self.repository.get_by_code(tag_in.tag_code)
        if existing:
            raise ValueError(f"Tag with code {tag_in.tag_code} already exists")
        
        obj_in_data = tag_in.model_dump()
        obj_in_data['id'] = str(uuid.uuid4())
        return await self.repository.create(obj_in_data)

    async def get_tag(self, tag_id: str) -> Optional[MetaTags]:
        return await self.repository.get(tag_id)

    async def get_all_tags(self, skip: int = 0, limit: int = 100) -> List[MetaTags]:
        return await self.repository.get_all(skip, limit)

    async def update_tag(self, tag_id: str, tag_in: MetaTagsUpdate) -> MetaTags:
        tag = await self.repository.get(tag_id)
        if not tag:
            raise ValueError("Tag not found")
        return await self.repository.update(tag, tag_in)

    async def delete_tag(self, tag_id: str) -> Optional[MetaTags]:
        return await self.repository.delete(tag_id)
