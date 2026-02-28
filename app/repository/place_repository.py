from repository.base_repository import BaseRepository
from db.models import Place
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class PlaceRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db=db, model=Place)

    async def get_place_duplicate(self, outside_id: int, project_id: id):
        result = await self.db.execute(select(self.model).filter(self.model.outside_id == outside_id, self.model.project_id == project_id))
        variable = result.scalars().first()
        if variable is None:
            return
        return variable
    
    async def get_by_project(self, project_id: int):
        result = await self.db.execute(select(self.model).filter(self.model.project_id == project_id))
        return result.scalars().all()