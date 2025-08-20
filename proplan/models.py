from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class Availability(str, Enum):
    FREE = "Free"
    BUSY = "Busy"


class Role(str, Enum):
    ADMIN = "Admin"
    MANAGER = "Manager"
    WORKER = "Worker"


class ProjectStatus(str, Enum):
    STARTED = "Started"
    ONGOING = "Ongoing"
    FINISHED = "Finished"


class TaskStatus(str, Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    DONE = "Done"


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
    end_time: datetime | None
    status: ProjectStatus = ProjectStatus.STARTED


class Task(BaseModel):
    id: int
    name: str
    start_time: datetime = datetime.utcnow
    end_time: datetime | None
    status: TaskStatus = TaskStatus.OPEN
    details: str | None
