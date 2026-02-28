from db.models import Project, Place
from schemas.travel_schema import ProjectBase, PlaceInputList, PlaceBase, PlaceVisited, ProjectUpdateRequest, PlaceUpdate
from repository.project_repository import ProjectRepository
from repository.place_repository import PlaceRepository
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from utils.outside_request import validate_artic_place

class ProjectService:
    def __init__(self, db: AsyncSession, project_repository: ProjectRepository):
        self.project_repository = project_repository
        self.place_repository = PlaceRepository(db)

    async def check_user_rights(self, project_id: int, user_id: int):
        project = await self.get_project(user_id, project_id)
        if project.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User has no access to current data")
        return

    async def create_place(self, user_id: int, place: PlaceBase, project_id: int, initial_create: bool = False):
        if not initial_create:
            if not validate_artic_place(place.outside_id):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place doesn`t exist")
            await self.check_user_rights(project_id, user_id)
            project = await self.project_repository.get_one(project_id)

            if project.project_status == True:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project is completed")
            
            places_count = await self.project_repository.get_places_number(project_id)

            if places_count == 10:
                raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Project can`t have more then 10 places")
            check_place = await self.place_repository.get_place_duplicate(place.outside_id, project_id)

            if check_place:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Place should be unique")
        
        db_place = Place(outside_id=place.outside_id, project_id=project_id, notes=place.notes)
        return await self.place_repository.create(db_place)
    
    async def visit_place(self, user_id: int, place_id: int):
        check_place = await self.place_repository.get_one(place_id)

        if check_place is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found")
        
        await self.check_user_rights(check_place.project_id, user_id)

        if check_place.is_visited == True:
            return {"message": "Place is already visited"}
        
        await self.place_repository.update(check_place, PlaceVisited(**{"is_visited": True}))

        project_status = await self.project_repository.get_not_visited_places(check_place.project_id)

        if project_status == True:
            await self.project_repository.complete_project(check_place.project_id)
        
        return {"message": "Place visit status updated"}
        

    async def create_project(self, project_create: ProjectBase, place_list: PlaceInputList, user_id: int):
        if project_create is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Data wasn`t given")

        project_places = []
        places_id = [place.outside_id for place in place_list.places]

        if len(place_list.places) < 1:
            raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Project can`t have less then 1 places")
        elif len(place_list.places) > 10:
            raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Project can`t have more then 10 places")
        elif len(place_list.places) != len(set(places_id)):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project places can`t be duplicates")

        for place_id in places_id:
            if not validate_artic_place(place_id):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place doesn`t exist")

        db_project = Project(name=project_create.name, description=project_create.description, start_date=project_create.start_date, user_id=user_id)
        created_project = await self.project_repository.create(db_project)

        for place in place_list.places:
            new_place = await self.create_place(user_id, place, created_project.id, True) 
            project_places.append(new_place)
        
        return {"project": created_project, "places": project_places}
    
    async def delete_project(self, user_id:int, project_id: int):
        await self.check_user_rights(project_id, user_id)
        project_to_delete = await self.project_repository.get_one(project_id)
        if project_to_delete is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project doesnt exist")
        return await self.project_repository.delete_project(project_to_delete)

    async def update_project(self, user_id: int, project_id: int, project_update: ProjectUpdateRequest):
        await self.check_user_rights(project_id, user_id)
        project = await self.project_repository.get_one(project_id)
        if project is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        return await self.project_repository.update(project, project_update)
    
    async def update_place(self, user_id:int, place_id: int, place_update: PlaceUpdate):
        place = await self.place_repository.get_one(place_id)
        await self.check_user_rights(place.project_id, user_id)
        if place is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found")
        return await self.place_repository.update(place, place_update)
    
    async def get_all_projects(self, user_id:int, offset: int = 0, limit: int = 10):
        return await self.project_repository.get_all_projects(user_id, offset=offset, limit=limit)

    async def get_project(self, user_id: int, project_id: int):
        project = await self.project_repository.get_one(project_id)
        if project is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        if project.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User has no access to current data")
        return project

    async def get_project_places(self, user_id:int, project_id: int):
        project = await self.project_repository.get_one(project_id)
        if project is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        if project.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User has no access to current data")
        return await self.place_repository.get_by_project(project_id)

    async def get_place(self, user_id: int, place_id: int):
        place = await self.place_repository.get_one(place_id)
        await self.check_user_rights(place.project_id, user_id)
        if place is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found")
        return place
