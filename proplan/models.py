from datetime import datetime

from pydantic import BaseModel

from proplan.enums import Role, Availability, ProjectStatus, TaskStatus


class User(BaseModel):
    id: int
    name: str
    email: str
    password: str
    role: Role
    availability: Availability


class Project(BaseModel):
    id: int
    name: str
    description: str
    start_time: datetime = datetime.utcnow
    end_time: datetime | None = None
    status: ProjectStatus = ProjectStatus.STARTED


class Task(BaseModel):
    id: int
    name: str
    start_time: datetime = datetime.utcnow
    end_time: datetime | None = None
    status: TaskStatus = TaskStatus.OPEN
    details: str | None = None
