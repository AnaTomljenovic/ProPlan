from enum import Enum

from pydantic import BaseModel


class Availability(str, Enum):
    FREE = "Free"
    BUSY = "Busy"


class Role(str, Enum):
    ADMIN = "Admin"
    MANAGER = "Manager"
    WORKER = "Worker"


class User(BaseModel):
    id: int
    name: str
    email: str
    password: str
    role: Role
    availability: Availability
