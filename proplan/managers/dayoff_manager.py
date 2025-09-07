from datetime import date
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from proplan.enums import DayOffType
from proplan.managers.notification_manager import NotificationManager
from fastapi import HTTPException

from proplan.models import Project, User, UserDayOff

class DayOffManager:
    def __init__(self, notifier: NotificationManager):
        self.notify = notifier

    async def create(self, session: AsyncSession, user: User, type: DayOffType, start_date: date, end_date: date) -> UserDayOff:
        if start_date > end_date:
            raise HTTPException(400, "start_date must be <= end_date")
        entry = UserDayOff(user_id=user.id, type=type, start_date=start_date, end_date=end_date)
        session.add(entry)
        await session.commit()
        await session.refresh(entry)

        result = await session.exec(select(Project).join(Project.workers).where(User.id == user.id))
        managers = []
        for p in result.all():
            if p.manager_id:
                m = await session.get(User, p.manager_id)
                if m:
                    managers.append(m)
        # using set to avoid duplicates
        managers_already_notified = set()
        for m in managers:
            if m.id in managers_already_notified: continue
            managers_already_notified.add(m.id)
            await self.notify.send_email(
                m.email,
                f"{user.name} reported {type.value} ({start_date} to {end_date})",
                f"User {user.name} ({user.email}) will be off from {start_date} to {end_date} ({type.value})."
            )
        return entry

    async def starting_today(self, session: AsyncSession, today: date):
        result = await session.exec(select(UserDayOff).where(UserDayOff.start_date == today))
        return result.all()
