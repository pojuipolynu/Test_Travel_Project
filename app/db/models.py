from datetime import date
from typing import Optional, List
from sqlalchemy import String, Integer, BigInteger, ForeignKey, DateTime, Boolean, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase

class Base(DeclarativeBase):
    pass


class BaseId(Base):
    __abstract__ = True
    id: Mapped[int] = mapped_column(Integer, primary_key=True)


class User(BaseId):
    __tablename__ = "users"
    email = mapped_column(String, unique=True, nullable=False)
    hashed_password = mapped_column(String, nullable=False)

    projects: Mapped[List["Project"]] = relationship("Project", back_populates="user")

class Project(BaseId):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="projects")

    project_status: Mapped[bool] = mapped_column(Boolean, default=False)

    places: Mapped[List["Place"]] = relationship("Place", back_populates="project", cascade="all, delete-orphan")

class Place(BaseId):
    __tablename__ = "places"
    
    outside_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    
    notes: Mapped[Optional[str]] = mapped_column(Text)
    is_visited: Mapped[bool] = mapped_column(Boolean, default=False)
    
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey('projects.id'), nullable=False)

    project: Mapped["Project"] = relationship("Project", back_populates="places")