from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from proplan.custom_models import ProjectCreate, ProjectUpdate
from proplan.enums import Role

from ..database import get_session
from ..models import User
from ..managers.project_manager import ProjectManager
from ..utils.users_dependency import get_current_user

router = APIRouter(prefix="/projects", tags=["projects"])
project_manager = ProjectManager()

@router.get("/")
async def list_projects(session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    return await project_manager.list(session, user)

@router.get("/{project_id}")
async def get_project(project_id: int, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    return await project_manager.get(session, project_id, user)

@router.post("/")
async def create_project(payload: ProjectCreate, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    if user.role != Role.ADMIN:
        raise HTTPException(403, "Admin only")
    return await project_manager.create(session, payload)

@router.put("/{project_id}")
async def update_project(project_id: int, payload: ProjectUpdate, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    if user.role != Role.ADMIN:
        raise HTTPException(403, "Admin only")
    return await project_manager.update(session, project_id, payload)

@router.delete("/{project_id}")
async def delete_project(project_id: int, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    if user.role != Role.ADMIN:
        raise HTTPException(403, "Admin only")
    await project_manager.delete(session, project_id)
    return {"ok": "Project deleted succesfully"}


