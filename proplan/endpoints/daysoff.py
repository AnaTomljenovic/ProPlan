from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from proplan.custom_models import DayOffCreate, DayOffOut
from proplan.database import get_session
from proplan.enums import Role
from proplan.managers.dayoff_manager import DayOffManager
from proplan.managers.notification_manager import NotificationManager
from proplan.models import Project, ProjectWorkerLink, User, UserDayOff
from proplan.utils.users_dependency import get_current_user


router = APIRouter(prefix="/days-off", tags=["days-off"])
manager = DayOffManager(NotificationManager())

@router.get("/me", response_model=List[DayOffOut])
async def list_my_days_off(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    result = await session.exec(select(UserDayOff).where(UserDayOff.user_id == user.id))
    return result.all()

@router.get("/user/{user_id}", response_model=List[DayOffOut])
async def list_user_days_off(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    if user.role == Role.WORKER and user.id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")

    result = await session.exec(select(UserDayOff).where(UserDayOff.user_id == user_id))
    return result.all()

@router.post("/", response_model=DayOffOut)
async def create_my_day_off(
    payload: DayOffCreate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    if payload.start_date > payload.end_date:
        raise HTTPException(status_code=400, detail="start_date must be <= end_date")

    entry = await manager.create(
        session=session,
        user=user,
        type=payload.type,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )
    return entry

@router.get("/project/{project_id}", response_model=List[DayOffOut])
async def list_project_days_off(
    project_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    if user.role == Role.WORKER:
        raise HTTPException(status_code=403, detail="Not allowed")

    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    user_ids_res = await session.exec(
        select(ProjectWorkerLink.user_id).where(ProjectWorkerLink.project_id == project_id)
    )
    user_ids = user_ids_res.all()
    if not user_ids:
        return []

    result = await session.exec(select(UserDayOff).where(UserDayOff.user_id.in_(user_ids)))
    return result.all()

@router.delete("/{entry_id}")
async def delete_day_off(
    entry_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    entry = await session.get(UserDayOff, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    # Workers may delete ONLY their own entries (managers/admin may delete any)
    if user.role == Role.WORKER and entry.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    # Prevent deleting past entries
    if entry.end_date < date.today() and user.role != Role.ADMIN:
        raise HTTPException(status_code=400, detail="Cannot delete past entries")

    await session.delete(entry)
    await session.commit()
    return {"ok": True, "note": "Days off were succesfully deleted"}
