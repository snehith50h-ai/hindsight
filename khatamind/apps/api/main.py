import json
from fastapi import FastAPI, APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any, List

from .deps import repos, action_repo, playbook_svc, ledger_svc, init_db

app = FastAPI(title="KhataMind API", version="0.1.0")

@app.on_event("startup")
def on_startup():
    init_db()

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
    # Mocking returning real actions from DB due to MVP scope of route definition
    return {"actions": []}

@v1_router.get("/customers/{id}/playbook")
async def get_playbook(id: str, tenant_id: str = "tenant-123"):
    playbook = await playbook_svc.generate_playbook(tenant_id, id)
    return {"customer_id": id, "playbook": playbook.model_dump()}

@v1_router.post("/actions/{id}/approve")
async def approve_action(id: str):
    # Retrieve action and execute
    return {"status": "approved", "action_id": id}

@v1_router.post("/actions/{id}/reject")
async def reject_action(id: str):
    return {"status": "rejected", "action_id": id}

@v1_router.post("/actions/{id}/edit")
async def edit_action(id: str, req: Dict[str, Any]):
    return {"status": "edited", "action_id": id, "new_payload": req}

app.include_router(v1_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
