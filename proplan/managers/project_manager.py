from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from proplan.enums import Role
from proplan.models import Project, User

class ProjectManager:
    async def list(self, session: AsyncSession, user: User):
        if user.role == Role.WORKER:
            raise HTTPException(status_code=403, detail="Workers cannot access projects")
        return (await session.exec(select(Project))).all()

    async def get(self, session: AsyncSession, project_id: int, user: User) -> Project:
        if user.role == Role.WORKER:
            raise HTTPException(status_code=403, detail="Workers cannot access projects")
        p = await session.get(Project, project_id)
        if not p:
            raise HTTPException(status_code=404, detail="Project not found")
        return p
