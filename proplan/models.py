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
