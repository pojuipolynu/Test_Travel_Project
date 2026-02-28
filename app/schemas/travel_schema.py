from pydantic import BaseModel, ConfigDict
from typing import List
from datetime import date

class PlaceBase(BaseModel):
    outside_id: int
    notes: str | None = None

class PlaceInputList(BaseModel):
    places: List[PlaceBase] | None = None

class PlaceUpdate(BaseModel):
    notes: str | None = None

class PlaceVisited(BaseModel):
    is_visited: bool | None = None

class ProjectBase(BaseModel):
    name: str
    description: str | None = None
    start_date: date | None = None

class Project(ProjectBase):
    id: int
    user_id: int
    project_status: bool
    model_config = ConfigDict(from_attributes=True)

class ProjectDetail(BaseModel):
    project: Project
    places: List[PlaceBase] | None = None

class ProjectUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    start_date: date | None = None

class ProjectsList(BaseModel):
    projects: List[Project]


class Place(PlaceBase):
    id: int
    project_id: int
    is_visited: bool 
    model_config = ConfigDict(from_attributes=True)