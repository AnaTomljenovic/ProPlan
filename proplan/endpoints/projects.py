from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from ..database import get_session
from ..models import User
from ..managers.project_manager import ProjectManager
from ..utils.users_dependency import get_current_user

router = APIRouter(prefix="/projects", tags=["projects"])
project_service = ProjectManager()

@router.get("/")
async def list_projects(session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    return await project_service.list(session, user)

@router.get("/{project_id}")
async def get_project(project_id: int, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    return await project_service.get(session, project_id, user)
