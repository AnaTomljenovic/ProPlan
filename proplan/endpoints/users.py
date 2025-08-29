from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from ..database import get_session
from ..models import User, Role
from ..custom_models import UserCreate, UserOut, UserUpdate
from ..managers.user_manager import UserManager
from ..utils.users_dependency import get_current_user

router = APIRouter(prefix="/users", tags=["users"])
manager = UserManager()

def _ensure_can_view(user: User, target_id: int):
    # Workers can only view themselves
    if user.role == Role.WORKER and user.id != target_id:
        raise HTTPException(status_code=403, detail="Not allowed")

@router.get("/", response_model=list[UserOut])
async def list_users(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    # Workers cannot list everyone
    if user.role == Role.WORKER:
        raise HTTPException(status_code=403, detail="Not allowed")
    return await manager.list(session)

@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    _ensure_can_view(user, user_id)
    return await manager.get(session, user_id)

@router.post("/", response_model=UserOut)
async def create_user(
    payload: UserCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Admin can create anyone; Manager can only create Worker → enforced in service too
    if current_user.role not in (Role.ADMIN, Role.MANAGER):
        raise HTTPException(status_code=403, detail="Not allowed")
    user = await manager.create(
        session=session,
        name=payload.name,
        email=payload.email,
        password=payload.password,
        availability=payload.availability,
        role=payload.role,
        requester_role=current_user.role,
    )
    return user

@router.put("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Workers can only update themselves
    if current_user.role == Role.WORKER and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")

    # The service enforces extra constraints for managers (e.g., cannot change role)
    user = await manager.update(
        session,
        user_id=user_id,
        requester_role=current_user.role,
        name=payload.name,
        availability=payload.availability,
        role=payload.role,
        password=payload.password,
    )
    return user

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Only admin can delete
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Admin only")
    await manager.delete(session, user_id)
    return {"ok": True, "note": "User was succesfully deleted"}
