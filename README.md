# 📌 ProPlan (Project Planning)

ProPlan is a **FastAPI + PostgreSQL demo app** for project planning.  
It demonstrates user roles, project/task management, days off handling, notifications, and scheduled reporting.

---

## ✨ Features

- **User Management**
  - Admin, Manager, Worker roles
  - CRUD for users
  - Role-based authorization

- **Project Management**
  - Create/update/delete projects
  - Assign/remove Managers
  - Assign/remove Workers
  - Project statuses: Started → Ongoing → Finished
  - Export monthly reports as CSV

- **Task Management**
  - Create/update/delete tasks
  - Assign/reassign/remove Workers
  - Task statuses: Open → In Progress → Done
  - Export tasks as CSV

- **Days Off**
  - Workers can request: Holiday, Sick Leave, Day Off
  - Validations: cannot assign users on leave
  - Managers receive email notifications
  - Daily reminder when leave starts

- **Notifications**
  - WebSocket for real-time updates
  - Emails via SMTP (Mailpit for dev)

- **Reports**
  - Monthly project reports emailed to Managers
  - Runs automatically on the 1st of each month, 06:00 UTC

---

## 🏗️ Architecture

- **FastAPI** backend with async SQLModel
- **PostgreSQL** database
- **Mailpit** SMTP for testing emails
- **Docker Compose** orchestrates services

---

## 🔧 Installation & Setup

The easiest way to run ProPlan is with Docker. This starts the application, PostgreSQL database, and Mailpit for testing emails.

```bash
docker compose up --build -d
```

This will start:  
- **db** → PostgreSQL on port `5432`  
- **app** → FastAPI backend on port `8000` → http://localhost:8000  
- **mailpit** → SMTP & inbox UI on port `8025` → http://localhost:8025  

---

### Initialize the Database with Mock Data

Run the seed command to create an Admin, Manager, Workers, Projects, and Tasks:

```bash
docker compose exec app uv run proplan-seed
```

### Reset the Database

If you need a clean database:

```bash
docker compose exec app uv run proplan-reset-db
```

---

### Access the API

- API docs: http://localhost:8000/docs  
- ReDoc: http://localhost:8000/redoc  
- Health check: http://localhost:8000/health  

---

### Default Accounts

- **Admin** → `admin@example.com` / `admin123`  
- **Manager** → `manager@example.com` / `manager123`  
- **Worker** → `worker1@example.com` / `worker123`

---

## 🛠️ Development Commands

```bash
# Run all containers
docker compose up --build -d

# Seed database with demo data
docker compose exec app uv run proplan-seed

# Reset database
docker compose exec app uv run proplan-reset-db

# View logs
docker compose logs -f app

# Run tests
docker compose exec app uv run pytest -q
```

---

## 👥 Roles & Permissions

- **Admin**
  - Manage users, projects, tasks
  - Assign managers/workers
  - Access everything

- **Manager**
  - Manage own projects & tasks
  - Assign workers to their projects
  - View workers’ days off

- **Worker**
  - View & update own tasks
  - Request days off
  - Cannot create projects or tasks

---

## 📧 Emails

- **Task/Project assignment** → Worker notified
- **Days off created** → Project Manager notified
- **Daily reminder** → Managers reminded of starting leaves
- **Monthly report** → Managers emailed project summary

(Mailpit UI: http://localhost:8025)

---

## ✅ Health Check

```bash
curl http://localhost:8000/health
# → { "ok": true }
```
