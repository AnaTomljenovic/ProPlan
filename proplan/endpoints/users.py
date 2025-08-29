from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from ..database import get_session
from ..models import User, Role
from ..custom_models import UserCreate, UserOut
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
