from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.responses import StreamingResponse
import csv, io
from proplan.database import get_session
from proplan.enums import Role
from proplan.managers.report_manager import ReportManager
from proplan.models import User
from proplan.utils.users_dependency import get_current_user

router = APIRouter(prefix="/reports", tags=["reports"])
report_manager = ReportManager()

@router.get("/projects/{project_id}/{year:int}/{month:int}")
async def monthly_report(project_id: int, year: int, month: int, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    if user.role not in (Role.ADMIN, Role.MANAGER):
        raise HTTPException(403, "Manager only")
    return await report_manager.json_report(session, project_id, year, month)

@router.get("/projects/{project_id}/{year:int}/{month:int}/export-csv")
async def monthly_report_csv(project_id: int, year: int, month: int, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    if user.role not in (Role.ADMIN, Role.MANAGER):
        raise HTTPException(403, "Manager only")
    rows = await report_manager.csv_rows(session, project_id, year, month)
    def generate():
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerows(rows)
        yield buffer.getvalue()
    return StreamingResponse(
        generate(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=project_{project_id}_{year}-{month:02d}.csv"}
    )
