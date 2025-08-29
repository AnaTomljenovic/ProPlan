from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from ..utils.users_dependency import verify_password, create_access_token
from ..models import User

class AuthManager:
    async def authenticate(self, session: AsyncSession, email: str, password: str) -> str:
        result = await session.exec(select(User).where(User.email == email))
        user = result.first()
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
        token = create_access_token({"sub": user.email, "role": user.role.value, "user_id": user.id})
        return token
