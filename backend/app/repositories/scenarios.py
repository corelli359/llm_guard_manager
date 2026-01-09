from typing import Optional
from sqlalchemy import select
from app.repositories.base import BaseRepository
from app.models.db_meta import Scenarios

class ScenariosRepository(BaseRepository[Scenarios]):
    async def get_by_app_id(self, app_id: str) -> Optional[Scenarios]:
        result = await self.db.execute(select(self.model).where(self.model.app_id == app_id))
        return result.scalars().first()
