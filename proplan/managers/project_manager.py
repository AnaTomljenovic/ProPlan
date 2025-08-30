from datetime import datetime
from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from proplan.enums import ProjectStatus, Role
from proplan.managers.notification_manager import NotificationManager
from proplan.models import Project, ProjectWorkerLink, User

class ProjectManager:
    def __init__(self, notifier: NotificationManager):
        self.notify = notifier

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

    async def assign_manager(self, session: AsyncSession, project_id: int, manager_id: int) -> None:
        project = await session.get(Project, project_id)
        manager = await session.get(User, manager_id)
        if not project or not manager:
            raise HTTPException(status_code=404, detail="Project or Manager not found")
        if manager.role != Role.MANAGER:
            raise HTTPException(status_code=400, detail="User is not a Manager")

        project.manager_id = manager.id
        session.add(project)
        await session.commit()

        # Ensure manager is a project member (via link table)
        existing = await session.exec(
            select(ProjectWorkerLink).where(
                ProjectWorkerLink.project_id == project.id,
                ProjectWorkerLink.user_id == manager.id,
            )
        )
        if not existing.first():
            session.add(ProjectWorkerLink(project_id=project.id, user_id=manager.id))
            await session.commit()

        await self.notify.send_email(
            manager.email,
            f"You are manager of project '{project.name}'",
            f"Hello {manager.name},\n\nYou have been assigned as manager of project '{project.name}'.",
        )

    async def remove_manager(self, session: AsyncSession, project_id: int) -> None:
        p = await session.get(Project, project_id)
        if not p:
            raise HTTPException(status_code=404, detail="Project not found")
        if p.status == ProjectStatus.ONGOING:
            raise HTTPException(status_code=400, detail="Cannot remove Manager while Project is Ongoing")
        p.manager_id = None
        session.add(p)
        await session.commit()

    async def add_worker(self, session: AsyncSession, project_id: int, worker_id: int, requester: User):
        if requester.role not in (Role.ADMIN, Role.MANAGER):
            raise HTTPException(status_code=403, detail="Not allowed")

        p = await session.get(Project, project_id)
        w = await session.get(User, worker_id)
        if not p or not w:
            raise HTTPException(status_code=404, detail="Project or Worker not found")
        if w.role != Role.WORKER:
            raise HTTPException(status_code=400, detail="Only users with role Worker can be added to a project")

        existing = await session.exec(
            select(ProjectWorkerLink).where(
                ProjectWorkerLink.project_id == p.id,
                ProjectWorkerLink.user_id == w.id,
            )
        )
        if existing.first():
            return {"ok": True, "note": "Worker already in project"}

        session.add(ProjectWorkerLink(project_id=p.id, user_id=w.id))
        await session.commit()

        await self.notify.send_email(
            w.email,
            f"Added to project '{p.name}'",
            f"Hello {w.name},\n\nYou have been added to project '{p.name}'.",
        )
        return {"ok": True, "note": "Worker assigned to project"}

    async def remove_worker(self, session: AsyncSession, project_id: int, worker_id: int, requester: User):
        if requester.role not in (Role.ADMIN, Role.MANAGER):
            raise HTTPException(status_code=403, detail="Not allowed")

        p = await session.get(Project, project_id)
        if not p:
            raise HTTPException(status_code=404, detail="Project not found")

        link_q = await session.exec(
            select(ProjectWorkerLink).where(
                ProjectWorkerLink.project_id == project_id,
                ProjectWorkerLink.user_id == worker_id,
            )
        )
        link = link_q.first()
        if not link:
            return {"ok": True, "note": "Worker not in project"}

        await session.delete(link)
        await session.commit()
        return {"ok": True, "note": "Worker removed from Project succesfully"}
