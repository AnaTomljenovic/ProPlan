# ProPlan (Project Planning) - FastAPI + SQLModel + Postgres

## quickstart
```bash
cp .env.example .env
docker compose build --no-cache
docker compose up -d
docker compose exec app uv run proplan-seed
```

This also adds mock up data which you can use for testing.

Admin user data you can use:
- email - admin@example.com
- pass - admin123

Open the following links after docker commands and mock up data added:
- http://localhost:8000/docs - for Swagger APIs
- http://localhost:8025/ - for tracking sent emails
