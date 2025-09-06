from fastapi import FastAPI

from proplan.endpoints import auth, projects, reports, tasks, users

app = FastAPI(title="ProPlan (Project Planning)")

@app.get("/health")
async def health():
    return {"ok": True}

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(reports.router)

def run():
    import uvicorn
    uvicorn.run("proplan.main:app", host="0.0.0.0", port=8000, reload=False)
