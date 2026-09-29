import json
import uuid
from fastapi import FastAPI, APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List

from .deps import repos, action_repo, playbook_svc, ledger_svc, init_db, get_session
from sqlmodel import Session, select
from core.domain.models import Action

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
async def get_actions(status: str = "proposed", session: Session = Depends(get_session)):
    from adapters.storage.sql_repos import ActionModel
    statement = select(ActionModel).where(ActionModel.status == status)
    results = session.exec(statement).all()
    return {"actions": [r.model_dump() for r in results]}

@v1_router.get("/customers/{id}/playbook")
async def get_playbook(id: str, tenant_id: str = "tenant-123"):
    playbook = await playbook_svc.generate_playbook(tenant_id, id)
    return {"customer_id": id, "playbook": playbook.model_dump()}

@v1_router.post("/actions/{id}/approve")
async def approve_action(id: str, session: Session = Depends(get_session)):
    from adapters.storage.sql_repos import ActionModel
    model = session.get(ActionModel, id)
    if not model:
        raise HTTPException(status_code=404, detail="Action not found")
    model.status = "approved"
    session.add(model)
    session.commit()
    return {"status": "approved", "action_id": id}

@v1_router.post("/actions/{id}/reject")
async def reject_action(id: str, session: Session = Depends(get_session)):
    from adapters.storage.sql_repos import ActionModel
    model = session.get(ActionModel, id)
    if not model:
        raise HTTPException(status_code=404, detail="Action not found")
    model.status = "rejected"
    session.add(model)
    session.commit()
    return {"status": "rejected", "action_id": id}

@v1_router.post("/actions/{id}/edit")
async def edit_action(id: str, req: Dict[str, Any], session: Session = Depends(get_session)):
    from adapters.storage.sql_repos import ActionModel
    model = session.get(ActionModel, id)
    if not model:
        raise HTTPException(status_code=404, detail="Action not found")
    model.payload_json = json.dumps(req)
    session.add(model)
    session.commit()
    return {"status": "edited", "action_id": id, "new_payload": req}

app.include_router(v1_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
