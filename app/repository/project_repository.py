from repository.base_repository import BaseRepository
from db.models import Project, Place
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

class ProjectRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db=db, model=Project)

        self.place_model = Place


    async def delete_project(self, project: Project):
        result = await self.db.execute(
            select(self.place_model).filter(self.place_model.project_id == project.id, self.place_model.is_visited == True)
        )
        visited_places = result.scalars().all() 

        if not visited_places:
            await self.db.delete(project)
            await self.db.commit()
            return {"message": "Project deleted"}
        
        return {"message": "Projects with visited places can`t be deleted"}

    async def get_places_number(self, project_id: int):
        places = select(func.count()).where(self.place_model.project_id == project_id)
        result = await self.db.execute(places)
        places_count = result.scalar() 
        return places_count
    
    async def get_not_visited_places(self, project_id: int):
        result = await self.db.execute(
            select(self.place_model).filter(self.place_model.project_id == project_id, self.place_model.is_visited == False)
        )
        visited_places = result.scalars().all() 

        if not visited_places: 
            return True
        
        return False
    
    async def complete_project(self, project_id: int):
        project = await self.get_one(project_id)
        project.project_status = True
    
        await self.db.commit()
        await self.db.refresh(project)
        return project
    
    async def get_all_projects(self, user_id:int, offset: int = 0, limit: int = 0):
        if limit == 0:
            result = await self.db.execute(select(self.model).filter(self.model.user_id==user_id).offset(offset))
        else:
            result = await self.db.execute(select(self.model).filter(self.model.user_id==user_id).offset(offset).limit(limit))
        projects = result.scalars().all()
        return projects