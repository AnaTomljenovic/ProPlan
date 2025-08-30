from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict

from proplan.enums import ProjectStatus
from .models import Role, Availability

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    availability: Availability
    role: Role
    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    availability: Availability = Availability.FREE
    role: Role = Role.WORKER

class UserUpdate(BaseModel):
    name: Optional[str] = None
    availability: Optional[Availability] = None
    role: Optional[Role] = None
    password: Optional[str] = None

class ProjectCreate(BaseModel):
    name: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    description: Optional[str] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
