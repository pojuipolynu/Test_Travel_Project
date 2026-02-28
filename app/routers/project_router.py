from fastapi import APIRouter, Depends, status
from schemas.travel_schema import Project, Place, ProjectBase, ProjectDetail, PlaceInputList, PlaceBase, ProjectUpdateRequest, PlaceUpdate

from services.authorization_service import AuthorizationService
from services.project_service import ProjectService

from utils.depends import get_project_service

router = APIRouter(prefix="/projects")

@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_projects(offset: int = 0, limit: int = 10, project_service: ProjectService = Depends(get_project_service), current_user=Depends(AuthorizationService.get_current_user)):
    return await project_service.get_all_projects(current_user.id, offset, limit)

@router.get("/{project_id}", response_model=Project, status_code=status.HTTP_200_OK)
async def get_project_by_id(project_id: int, project_service: ProjectService = Depends(get_project_service), current_user=Depends(AuthorizationService.get_current_user)):
    return await project_service.get_project(current_user.id, project_id)

@router.get("/{project_id}/places", status_code=status.HTTP_200_OK)
async def get_project_places(project_id: int, project_service: ProjectService = Depends(get_project_service), current_user=Depends(AuthorizationService.get_current_user)):
    return await project_service.get_project_places(current_user.id, project_id)

@router.post("/create", response_model=ProjectDetail, status_code=status.HTTP_201_CREATED)
async def create_project(project_create: ProjectBase, place_list: PlaceInputList, project_service: ProjectService = Depends(get_project_service), current_user=Depends(AuthorizationService.get_current_user)):
    return await project_service.create_project(project_create, place_list, current_user.id)

@router.delete("/delete/{project_id}", status_code=status.HTTP_200_OK)
async def delete_project(project_id: int, project_service: ProjectService = Depends(get_project_service), current_user=Depends(AuthorizationService.get_current_user)):
    return await project_service.delete_project(current_user.id, project_id)

@router.post("/project/{project_id}", status_code=status.HTTP_200_OK)
async def add_place(project_id: int, place: PlaceBase, project_service: ProjectService = Depends(get_project_service), current_user=Depends(AuthorizationService.get_current_user)):
    return await project_service.create_place(current_user.id, place, project_id)

@router.put("/project/{project_id}", response_model=Project, status_code=status.HTTP_200_OK)
async def update_project(project_id: int, project_updated: ProjectUpdateRequest, project_service: ProjectService = Depends(get_project_service), current_user=Depends(AuthorizationService.get_current_user)):
    return await project_service.update_project(current_user.id, project_id, project_updated)

@router.post("/place/{place_id}", status_code=status.HTTP_200_OK)
async def visit_place(place_id: int, project_service: ProjectService = Depends(get_project_service), current_user=Depends(AuthorizationService.get_current_user)):
    return await project_service.visit_place(current_user.id, place_id)

@router.put("/place/{place_id}", status_code=status.HTTP_200_OK)
async def update_place(place_id: int, place_update: PlaceUpdate, project_service: ProjectService = Depends(get_project_service), current_user=Depends(AuthorizationService.get_current_user)):
    return await project_service.update_place(current_user.id, place_id, place_update)

@router.get("/place/{place_id}", response_model=Place, status_code=status.HTTP_200_OK)
async def get_place_by_id(place_id: int, project_service: ProjectService = Depends(get_project_service), current_user=Depends(AuthorizationService.get_current_user)):
    return await project_service.get_place(current_user.id, place_id)