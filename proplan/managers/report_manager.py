from datetime import date, datetime
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException
from ..models import Project, Task

class ReportManager:
    def _validate_month(self, year: int, month: int) -> tuple[datetime, datetime]:
        if month < 1 or month > 12:
            raise HTTPException(400, "Month must be 1..12")
        today = date.today()
        first_of_request = date(year, month, 1)
        first_of_current = today.replace(day=1)
        if first_of_request >= first_of_current:
            if first_of_request == first_of_current:
                raise HTTPException(400, "Cannot request current month")
            raise HTTPException(400, "Cannot request future month")
        if month == 12:
            next_first = date(year + 1, 1, 1)
        else:
            next_first = date(year, month + 1, 1)
        start_dt = datetime(first_of_request.year, first_of_request.month, 1)
        end_dt = datetime(next_first.year, next_first.month, 1)
        return start_dt, end_dt

    async def json_report(self, session: AsyncSession, project_id: int, year: int, month: int) -> dict:
        start_dt, end_dt = self._validate_month(year, month)
        p = await session.get(Project, project_id)
        if not p:
            raise HTTPException(404, "Project not found")
        result = await session.exec(
            select(Task).where(Task.project_id == project_id, Task.start_time >= start_dt, Task.start_time < end_dt)
        )
        tasks = result.all()
        return {
            "project_id": p.id,
            "project_name": p.name,
            "year": year,
            "month": month,
            "count": len(tasks),
            "tasks": [{"id": t.id, "name": t.name, "status": t.status.value, "start_time": t.start_time.isoformat() if t.start_time else ""} for t in tasks],
        }

    async def csv_rows(self, session: AsyncSession, project_id: int, year: int, month: int) -> list[list[str]]:
        start_dt, end_dt = self._validate_month(year, month)
        result = await session.exec(
            select(Task).where(Task.project_id == project_id, Task.start_time >= start_dt, Task.start_time < end_dt)
        )
        tasks = result.all()
        rows = [["id", "name", "status", "start_time"]]
        for t in tasks:
            rows.append([str(t.id), t.name, t.status.value, t.start_time.isoformat() if t.start_time else ""])
        return rows
