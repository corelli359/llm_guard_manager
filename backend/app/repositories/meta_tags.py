from typing import List, Optional
from sqlalchemy import select
from app.repositories.base import BaseRepository
from app.models.db_meta import MetaTags

class MetaTagsRepository(BaseRepository[MetaTags]):
    async def get_by_code(self, tag_code: str) -> Optional[MetaTags]:
        result = await self.db.execute(select(self.model).where(self.model.tag_code == tag_code))
        return result.scalars().first()
    
    async def get_root_tags(self) -> List[MetaTags]:
        result = await self.db.execute(select(self.model).where(self.model.parent_code == None))
        return result.scalars().all()
