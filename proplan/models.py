from datetime import datetime
from typing import List, Optional

from sqlmodel import SQLModel, Field, Relationship, Column, String


from proplan.enums import Role, Availability, ProjectStatus, TaskStatus


class ProjectWorkerLink(SQLModel, table=True):
    __tablename__ = "project_workers"
    project_id: Optional[int] = Field(default=None, foreign_key="project.id", primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)


class TaskWorkerLink(SQLModel, table=True):
    __tablename__ = "task_workers"
    task_id: Optional[int] = Field(default=None, foreign_key="task.id", primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(sa_column=Column(String, unique=True, index=True, nullable=False))
    password_hash: str = Field(exclude=True)
    availability: Availability = Field(default=Availability.FREE)
    role: Role = Field(default=Role.WORKER)

    projects: List["Project"] = Relationship(back_populates="workers", link_model=ProjectWorkerLink)
    tasks: List["Task"] = Relationship(back_populates="workers", link_model=TaskWorkerLink)


class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: datetime | None = None
    description: str | None = None
    status: ProjectStatus = Field(default=ProjectStatus.STARTED)

    manager_id: Optional[int] = Field(default=None, foreign_key="user.id")

    workers: List[User] = Relationship(back_populates="projects", link_model=ProjectWorkerLink)
    tasks: List["Task"] = Relationship(back_populates="project")


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    status: TaskStatus = Field(default=TaskStatus.OPEN)
    details: Optional[str] = None

    project_id: int = Field(foreign_key="project.id")
    project: Optional["Project"] = Relationship(back_populates="tasks")

    workers: List["User"] = Relationship(back_populates="tasks", link_model=TaskWorkerLink)
