from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..models import (
    Task, Project, User, TaskStatus, Role,
    TaskWorkerLink,
)
from .notification_manager import NotificationManager

class TaskService:
    def __init__(self, notifier: NotificationManager):
        self.notify = notifier

    async def _ensure_worker_available(self, session: AsyncSession, worker: User):
        # one task per worker
        existing_task_link = await session.exec(
            select(TaskWorkerLink).where(TaskWorkerLink.user_id == worker.id)
        )
        if existing_task_link.first():
            raise HTTPException(400, "Worker is already assigned to another task")

    async def list(self, session: AsyncSession, requester: User):
        if requester.role == Role.WORKER:
            # tasks for this worker via link table
            task_ids = await session.exec(
                select(TaskWorkerLink.task_id).where(TaskWorkerLink.user_id == requester.id)
            )
            ids = task_ids.all()
            if not ids:
                return []
            result = await session.exec(select(Task).where(Task.id.in_(ids)))
            return result.all()
        result = await session.exec(select(Task))
        return result.all()

    async def create(self, session: AsyncSession, payload) -> Task:
        proj = await session.get(Project, payload.project_id)
        if not proj:
            raise HTTPException(404, "Project not found")
        from datetime import datetime as dt
        t = Task(
            name=payload.name,
            start_time=None if payload.start_time is None else dt.fromisoformat(payload.start_time),
            end_time=None if payload.end_time is None else dt.fromisoformat(payload.end_time),
            details=payload.details,
            project_id=payload.project_id,
            status=TaskStatus.OPEN,
        )
        session.add(t)
        await session.commit()
        await session.refresh(t)
        return t

    async def get(self, session: AsyncSession, task_id: int, requester: User) -> Task:
        t = await session.get(Task, task_id)
        if not t:
            raise HTTPException(404, "Task not found")
        if requester.role == Role.WORKER:
            # verify worker is linked to task (no t.workers access)
            link = await session.exec(
                select(TaskWorkerLink).where(
                    TaskWorkerLink.task_id == task_id,
                    TaskWorkerLink.user_id == requester.id,
                )
            )
            if not link.first():
                raise HTTPException(403, "Not allowed")
        return t

    async def update(self, session: AsyncSession, task_id: int, payload) -> Task:
        t = await session.get(Task, task_id)
        if not t:
            raise HTTPException(404, "Task not found")
        if payload.status is not None and t.status == TaskStatus.DONE and payload.status != TaskStatus.DONE:
            raise HTTPException(400, "Cannot move a Done task back to another state")
        from datetime import datetime as dt
        if payload.name is not None: t.name = payload.name
        if payload.start_time is not None: t.start_time = dt.fromisoformat(payload.start_time)
        if payload.end_time is not None: t.end_time = dt.fromisoformat(payload.end_time)
        if payload.status is not None: t.status = payload.status
        if payload.details is not None: t.details = payload.details
        session.add(t)
        await session.commit()
        await session.refresh(t)
        return t

    async def delete(self, session: AsyncSession, task_id: int) -> None:
        t = await session.get(Task, task_id)
        if not t:
            raise HTTPException(404, "Task not found")
        await session.delete(t)
        await session.commit()
