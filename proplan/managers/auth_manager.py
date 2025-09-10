from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from proplan.models import User
from proplan.utils.users_dependency import create_access_token, verify_password


class AuthManager:
    async def authenticate(self, session: AsyncSession, email: str, password: str) -> str:
        result = await session.exec(select(User).where(User.email == email))
        user = result.first()
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
        token = create_access_token({"sub": user.email, "role": user.role.value, "user_id": user.id})
        return token
