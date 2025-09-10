from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException

from proplan.enums import Availability, Role
from proplan.models import User
from proplan.utils.users_dependency import get_password_hash


class UserManager:
    async def list(self, session: AsyncSession) -> list[User]:
        result = await session.exec(select(User))
        return result.all()

    async def get(self, session: AsyncSession, user_id: int) -> User:
        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(404, "User not found")
        return user

    async def create(
        self, session: AsyncSession, name: str, email: str, password: str,
        availability: Availability, role: Role, requester_role: Role
    ) -> User:
        if requester_role == Role.MANAGER and role != Role.WORKER:
            raise HTTPException(403, "Managers may only create Worker accounts")
        exists = await session.exec(select(User).where(User.email == email))
        if exists.first():
            raise HTTPException(400, "Email already registered")
        user = User(
            name=name, email=email, password_hash=get_password_hash(password),
            availability=availability, role=role
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def update(self, session: AsyncSession, user_id: int, requester_role: Role, **fields) -> User:
        user = await self.get(session, user_id)
        if requester_role == Role.MANAGER and fields.get("role") and fields.get("role") != user.role:
            raise HTTPException(403, "Managers cannot change roles")
        if "password" in fields and fields["password"] is not None:
            user.password_hash = get_password_hash(fields.pop("password"))
        for k, v in list(fields.items()):
            if v is not None and hasattr(user, k):
                setattr(user, k, v)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def delete(self, session: AsyncSession, user_id: int) -> None:
        user = await self.get(session, user_id)
        await session.delete(user)
        await session.commit()
