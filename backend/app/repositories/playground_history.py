from typing import List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.db_meta import PlaygroundHistory

class PlaygroundHistoryRepository(BaseRepository[PlaygroundHistory]):
    def __init__(self, db: AsyncSession):
        super().__init__(PlaygroundHistory, db)

    async def get_history(
        self,
        skip: int,
        limit: int,
        playground_type: Optional[str] = None,
        app_id: Optional[str] = None
    ) -> List[PlaygroundHistory]:
        stmt = select(self.model)

        if playground_type:
            stmt = stmt.where(self.model.playground_type == playground_type)
        
        if app_id:
            stmt = stmt.where(self.model.app_id == app_id)
            
        stmt = stmt.order_by(desc(self.model.created_at))
        stmt = stmt.offset(skip).limit(limit)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
