from fastapi import FastAPI

app = FastAPI(title="ProPlan (Project Planning)")


@app.get("/health")
async def health():
    return {"ok": True}
