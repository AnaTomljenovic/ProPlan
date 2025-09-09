from datetime import date
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from proplan.managers.dayoff_manager import DayOffManager
from proplan.managers.notification_manager import NotificationManager
from ..database import async_session_factory
from ..config import DAILY_REMINDER_HOUR

from ..models import User, Project
from sqlmodel import select

class SchedulerManager:
    def __init__(self, notifier: NotificationManager, dayoff: DayOffManager):
        self.scheduler = AsyncIOScheduler()
        self.notifier = notifier
        self.dayoff = dayoff

    async def _send_start_reminders(self):
        async with async_session_factory() as session:
            today = date.today()
            entries = await self.dayoff.starting_today(session, today)
            for entry in entries:
                user = await session.get(User, entry.user_id)
                result = await session.exec(select(Project).join(Project.workers).where(User.id == user.id))
                managers = []
                for p in result.all():
                    if p.manager_id:
                        m = await session.get(User, p.manager_id)
                        if m:
                            managers.append(m)
                sent = set()
                for m in managers:
                    if m.id in sent: continue
                    sent.add(m.id)
                    await self.notifier.send_email(
                        m.email,
                        f"Reminder: {user.name} starts {entry.type.value} today",
                        f"User {user.name} ({user.email}) is off from {entry.start_date} to {entry.end_date} ({entry.type.value})."
                    )

    def start(self):
        trigger = CronTrigger(hour=DAILY_REMINDER_HOUR, minute=0)
        self.scheduler.add_job(self._send_start_reminders, trigger)
        self.scheduler.start()
