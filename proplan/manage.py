import asyncio
import typer
from faker import Faker
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from proplan.utils.users_dependency import get_password_hash
from proplan.database import async_session_factory, init_db
from proplan.models import (
    User, Project, Task,
    Role, ProjectStatus, TaskStatus,
    ProjectWorkerLink, TaskWorkerLink,
)

cli = typer.Typer(help="Management commands for ProPlan")

async def seed_users(session: AsyncSession):
    fake = Faker()
    admin = (await session.exec(select(User).where(User.email == "admin@example.com"))).first()
    if not admin:
        admin = User(
            name="Admin",
            email="admin@example.com",
            password_hash=get_password_hash("admin123"),
            role=Role.ADMIN,
        )
        session.add(admin)

    manager = (await session.exec(select(User).where(User.email == "manager@example.com"))).first()
    if not manager:
        manager = User(
            name="Manager Mike",
            email="manager@example.com",
            password_hash=get_password_hash("manager123"),
            role=Role.MANAGER,
        )
        session.add(manager)

    for i in range(5):
        email = f"worker{i+1}@example.com"
        exists = (await session.exec(select(User).where(User.email == email))).first()
        if not exists:
            session.add(
                User(
                    name=fake.name(),
                    email=email,
                    password_hash=get_password_hash("worker123"),
                    role=Role.WORKER,
                )
            )

    await session.commit()

async def seed_projects_and_tasks(session: AsyncSession):
    manager = (await session.exec(select(User).where(User.email == "manager@example.com"))).first()
    workers = (await session.exec(select(User).where(User.role == Role.WORKER))).all()

    proj = Project(
        name="Building site industrial zone - IGH",
        description="Contract with IGH for industrial building",
        status=ProjectStatus.STARTED,
        manager_id=manager.id if manager else None,
    )
    session.add(proj)
    await session.commit()
    await session.refresh(proj)

    # Manager should also be a member of the project
    if manager:
        session.add(ProjectWorkerLink(project_id=proj.id, user_id=manager.id))
        await session.commit()

    t1 = Task(
        name="Building site - first visit",
        details="Visit and preview of building site",
        project_id=proj.id,
        status=TaskStatus.OPEN,
    )
    t2 = Task(
        name="Mobile office",
        details="Transport and set up mobile home on building site",
        project_id=proj.id,
        status=TaskStatus.OPEN,
    )
    t3 = Task(
        name="Initial excavation",
        details="Per project start excavation",
        project_id=proj.id,
        status=TaskStatus.OPEN,
    )
    session.add(t1)
    session.add(t2)
    session.add(t3)
    await session.commit()
    await session.refresh(t1)
    await session.refresh(t2)
    await session.refresh(t3)

    # Assign workers using link rows (avoid touching relationship collections)
    if workers:
        # Assign first worker to t1
        session.add(TaskWorkerLink(task_id=t1.id, user_id=workers[0].id))
        # Next two workers to t2 (if present)
        for w in workers[1:3]:
            session.add(TaskWorkerLink(task_id=t2.id, user_id=w.id))
        await session.commit()

@cli.command("seed")
def seed_command():
    async def _run():
        await init_db()
        async with async_session_factory() as session:
            await seed_users(session)
            await seed_projects_and_tasks(session)
        print("Mock data generated. Admin: admin@example.com / admin123")
    asyncio.run(_run())

@cli.command("reset-db")
def reset_db_command():
    """Drop all tables and recreate them (DANGER: wipes all data)."""
    async def _run():
        from proplan.database import engine
        # Drop & recreate
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
            await conn.run_sync(SQLModel.metadata.create_all)
        print("Database wiped and recreated.")
    asyncio.run(_run())

if __name__ == "__main__":
    cli()
