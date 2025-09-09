from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from proplan.custom_models import ProjectCreate, ProjectUpdate
from proplan.enums import Role
from proplan.managers.notification_manager import NotificationManager

from ..database import get_session
from ..models import User
from ..managers.project_manager import ProjectManager
from ..utils.users_dependency import get_current_user

router = APIRouter(prefix="/projects", tags=["projects"])
project_manager = ProjectManager(NotificationManager())

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

@router.post("/{project_id}/assign-manager/{manager_id}")
async def assign_manager(project_id: int, manager_id: int, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    if user.role != Role.ADMIN:
        raise HTTPException(403, "Admin only")
    await project_manager.assign_manager(session, project_id, manager_id)
    return {"ok": "Manager assigned to Project succesfully"}

@router.post("/{project_id}/remove-manager")
async def remove_manager(project_id: int, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    if user.role != Role.ADMIN:
        raise HTTPException(403, "Admin only")
    await project_manager.remove_manager(session, project_id)
    return {"ok": "Manager removed from Project succesfully"}

@router.post("/{project_id}/assign-worker/{worker_id}")
async def assign_worker_to_project(
    project_id: int,
    worker_id: int,
    session: AsyncSession = Depends(get_session),
    me: User = Depends(get_current_user),
):
    return await project_manager.add_worker(session, project_id, worker_id, me)

@router.post("/{project_id}/remove-worker/{worker_id}")
async def remove_worker_from_project(
    project_id: int,
    worker_id: int,
    session: AsyncSession = Depends(get_session),
    me: User = Depends(get_current_user),
):
    return await project_manager.remove_worker(session, project_id, worker_id, me)

