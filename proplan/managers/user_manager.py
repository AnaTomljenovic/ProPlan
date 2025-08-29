from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Depends, HTTPException, status

from proplan.enums import Availability, Role
from proplan.utils.users_dependency import get_password_hash
from ..database import get_session
from ..config import JWT_SECRET, JWT_ALGORITHM
from ..models import User

class UserManager:
    async def list(self, session: AsyncSession) -> list[User]:
        result = await session.exec(select(User))
        return result.all()

    async def get(self, session: AsyncSession, user_id: int) -> User:
        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(404, "User not found")
        return user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: int | None = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await session.get(User, user_id)
    if user is None:
        raise credentials_exception
    return user
