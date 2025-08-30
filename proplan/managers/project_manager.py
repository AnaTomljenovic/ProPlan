from datetime import datetime
from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from proplan.enums import ProjectStatus, Role
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

    async def create(self, session: AsyncSession, payload) -> Project:
        p = Project(
            name=payload.name,
            start_time=datetime.fromisoformat(payload.start_time) if payload.start_time else None,
            end_time=datetime.fromisoformat(payload.end_time) if payload.end_time else None,
            description=payload.description,
            status=ProjectStatus.STARTED,
        )
        session.add(p)
        await session.commit()
        await session.refresh(p)
        return p

    async def update(self, session: AsyncSession, project_id: int, payload) -> Project:
        p = await session.get(Project, project_id)
        if not p:
            raise HTTPException(status_code=404, detail="Project not found")
        if payload.status is not None and p.status == ProjectStatus.FINISHED and payload.status != ProjectStatus.FINISHED:
            raise HTTPException(status_code=400, detail="Cannot move a Finished project back to another state")
        from datetime import datetime as dt
        if payload.name is not None:
            p.name = payload.name
        if payload.start_time is not None:
            p.start_time = dt.fromisoformat(payload.start_time)
        if payload.end_time is not None:
            p.end_time = dt.fromisoformat(payload.end_time)
        if payload.description is not None:
            p.description = payload.description
        if payload.status is not None:
            p.status = payload.status
        session.add(p)
        await session.commit()
        await session.refresh(p)
        return p

    async def delete(self, session: AsyncSession, project_id: int) -> None:
        p = await session.get(Project, project_id)
        if not p:
            raise HTTPException(status_code=404, detail="Project not found")
        await session.delete(p)
        await session.commit()
