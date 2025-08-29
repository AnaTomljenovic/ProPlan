from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from .models import Role, Availability

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
