from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import postgres_db
from services.authorization_service import AuthorizationService
from services.project_service import ProjectService
from repository.user_repository import UserRepository
from repository.project_repository import ProjectRepository
from typing import Annotated

def get_authorization_service(db: Annotated[AsyncSession, Depends(postgres_db)]):
    user_repository = UserRepository(db)
    return AuthorizationService(user_repository)

def get_project_service(db: Annotated[AsyncSession, Depends(postgres_db)]):
    project_repository = ProjectRepository(db)
    return ProjectService(db=db, project_repository=project_repository)