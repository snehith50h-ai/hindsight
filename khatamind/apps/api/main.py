from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from typing import Dict, Any

app = FastAPI(title="KhataMind API", version="0.1.0")

v1_router = APIRouter(prefix="/v1")

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/readyz")
async def readyz():
    # In a full implementation, check DB, memory, LLM connectivity here
    return {"status": "ready"}

class TenantCreate(BaseModel):
    name: str
    city: str

@v1_router.post("/tenants")
async def create_tenant(req: TenantCreate):
    return {"status": "created", "tenant_id": "tenant-123"}

@v1_router.post("/sim/runs")
async def start_sim_run(req: Dict[str, Any]):
    return {"status": "started", "run_id": "run-456"}

@v1_router.get("/actions")
async def get_actions(status: str = "proposed"):
    return {"actions": []}

app.include_router(v1_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
