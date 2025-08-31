from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from proplan.custom_models import TaskCreate, TaskUpdate
from proplan.database import get_session
from proplan.enums import Role
from proplan.managers.notification_manager import NotificationManager
from proplan.managers.task_manager import TaskManager
from proplan.models import User
from proplan.utils.users_dependency import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])
task_manager = TaskManager(NotificationManager())

@router.get("/")
async def list_tasks(session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    return await task_manager.list(session, user)

@router.post("/")
async def create_task(payload: TaskCreate, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    if user.role not in (Role.ADMIN, Role.MANAGER):
        raise HTTPException(403, "Manager only")
    return await task_manager.create(session, payload)

@router.get("/{task_id}")
async def get_task(task_id: int, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    return await task_manager.get(session, task_id, user)

@router.put("/{task_id}")
async def update_task(task_id: int, payload: TaskUpdate, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    if user.role not in (Role.ADMIN, Role.MANAGER):
        raise HTTPException(403, "Manager only")
    return await task_manager.update(session, task_id, payload)

@router.delete("/{task_id}")
async def delete_task(task_id: int, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    if user.role not in (Role.ADMIN, Role.MANAGER):
        raise HTTPException(403, "Manager only")
    await task_manager.delete(session, task_id)
    return {"ok": True, "note": "Task deleted succesfully"}

@router.post("/{task_id}/assign-worker/{worker_id}")
async def assign_worker(task_id: int, worker_id: int, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    if user.role not in (Role.ADMIN, Role.MANAGER):
        raise HTTPException(403, "Manager only")
    return await task_manager.assign_worker(session, task_id, worker_id)

@router.post("/{task_id}/remove-worker/{worker_id}")
async def remove_worker(task_id: int, worker_id: int, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    if user.role not in (Role.ADMIN, Role.MANAGER):
        raise HTTPException(403, "Manager only")
    return await task_manager.remove_worker(session, task_id, worker_id)

@router.post("/{task_id}/reassign-worker/{old_worker_id}/{new_worker_id}")
async def reassign_worker(task_id: int, old_worker_id: int, new_worker_id: int, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    if user.role not in (Role.ADMIN, Role.MANAGER):
        raise HTTPException(403, "Manager only")
    return await task_manager.reassign_worker(session, task_id, old_worker_id, new_worker_id)
