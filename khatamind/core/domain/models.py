from datetime import timezone
from datetime import datetime
from typing import Literal, Optional, List, Dict, Any
from pydantic import BaseModel, Field

class Tenant(BaseModel):
    id: str
    name: str
    city: str
    timezone: str = "Asia/Kolkata"
    cost_of_capital_pa: float = 0.18
    max_discount_pct: float = 2.0
    autonomy_default: Literal["observe", "suggest", "auto"] = "suggest"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Customer(BaseModel):
    id: str
    tenant_id: str
    name: str
    contact_person: str
    phone: str
    language: Literal["en", "hi", "te", "hinglish"] = "en"
    segment: str
    credit_limit_paise: int
    is_business_buyer: bool
    opted_out: bool = False
    preferred_contact_hint: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Invoice(BaseModel):
    id: str
    tenant_id: str
    customer_id: str
    number: str
    issued_on: datetime
    due_on: datetime
    amount_paise: int
    paid_paise: int = 0
    status: Literal["open", "partial", "paid", "disputed", "written_off"]
    po_ref: Optional[str] = None

class Payment(BaseModel):
    id: str
    invoice_id: str
    amount_paise: int
    received_on: datetime
    method: Literal["upi", "bank", "cash", "cheque"]

class OrderItem(BaseModel):
    sku: str
    qty: int
    value_paise: int

class Order(BaseModel):
    id: str
    customer_id: str
    placed_on: datetime
    items: List[OrderItem]
    total_paise: int

class Interaction(BaseModel):
    id: str
    customer_id: str
    ts: datetime
    direction: Literal["out", "in"]
    channel: Literal["whatsapp", "sms", "call", "visit", "email"]
    kind: Literal["reminder", "promise", "reply", "complaint", "dispute", "thanks", "offer", "nudge", "note"]
    text: str
    meta: Dict[str, Any] = Field(default_factory=dict)
    action_id: Optional[str] = None

class Promise(BaseModel):
    id: str
    customer_id: str
    invoice_ids: List[str]
    promised_on: datetime
    promised_for: datetime
    amount_paise: int
    status: Literal["pending", "kept", "broken", "partial"]
    resolved_on: Optional[datetime] = None

class Action(BaseModel):
    id: str
    tenant_id: str
    customer_id: str
    skill: str
    type: Literal["SEND_MESSAGE", "CREATE_TASK", "ALERT_OWNER", "OFFER_INCENTIVE", "HOLD_CREDIT", "PAUSE_DUNNING"]
    payload: Dict[str, Any]
    rationale: str
    evidence_memory_ids: List[str] = Field(default_factory=list)
    priority: float
    expected_value_paise: int
    status: Literal["proposed", "delayed", "awaiting_approval", "approved", "executed", "rejected", "denied", "expired"]
    dedupe_key: str
    not_before: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    executed_at: Optional[datetime] = None

class Outcome(BaseModel):
    id: str
    action_id: str
    observed_at: datetime
    kind: Literal["paid", "partial", "promise", "replied", "ignored", "reordered", "churned", "disputed"]
    value_paise: int
    days_to_effect: int

class TacticStat(BaseModel):
    tenant_id: str
    customer_id: str
    tactic_key: str
    trials: int
    successes: int
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PlaybookField(BaseModel):
    value: Any
    confidence: Literal["learning", "high"]
    evidence_ids: List[str] = Field(default_factory=list)

class Playbook(BaseModel):
    customer_id: str
    version: int
    channel: Optional[PlaybookField] = None
    best_hours: Optional[PlaybookField] = None
    tone: Optional[PlaybookField] = None
    language: Optional[PlaybookField] = None
    incentive_response: Optional[PlaybookField] = None
    approver: Optional[PlaybookField] = None
    promise_reliability: Optional[PlaybookField] = None
    reorder_cycle_days: Optional[PlaybookField] = None
    interests: Optional[PlaybookField] = None
    cautions: Optional[PlaybookField] = None
    evidence_memory_ids: List[str] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DecisionTrace(BaseModel):
    id: str
    action_id: str
    recalled: List[str]
    rules_fired: List[str]
    llm_model: str
    prompt_version: str
    latency_ms: int

class JobRun(BaseModel):
    job: str
    window_key: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    status: Literal["running", "success", "failed"]

class AutonomyRule(BaseModel):
    tenant_id: str
    scope: Literal["global", "skill", "customer"]
    scope_id: str
    level: Literal["observe", "suggest", "auto"]
    paused: bool
    daily_cap: int
