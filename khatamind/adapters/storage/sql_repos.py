from datetime import datetime, timedelta, timezone
from typing import List, Optional
from sqlmodel import SQLModel, Field, Session, select
from core.domain.models import Customer, Invoice, Action, TacticStat

# Base SQLModel tables mappings for MVP features
class CustomerModel(SQLModel, table=True):
    id: str = Field(primary_key=True)
    tenant_id: str
    name: str
    contact_person: str
    phone: str
    language: str
    segment: str
    credit_limit_paise: int
    is_business_buyer: bool
    opted_out: bool = False
    preferred_contact_hint: Optional[str] = None
    created_at: datetime

class InvoiceModel(SQLModel, table=True):
    id: str = Field(primary_key=True)
    tenant_id: str
    customer_id: str
    number: str
    issued_on: datetime
    due_on: datetime
    amount_paise: int
    paid_paise: int
    status: str
    po_ref: Optional[str] = None

class ActionModel(SQLModel, table=True):
    id: str = Field(primary_key=True)
    tenant_id: str
    customer_id: str
    skill: str
    type: str
    payload_json: str
    rationale: str
    expected_value_paise: int
    status: str
    dedupe_key: str
    priority: float
    not_before: Optional[datetime] = None
    created_at: datetime
    executed_at: Optional[datetime] = None

class TacticStatModel(SQLModel, table=True):
    tenant_id: str = Field(primary_key=True)
    customer_id: str = Field(primary_key=True)
    tactic_key: str = Field(primary_key=True)
    trials: int
    successes: int
    last_updated: datetime

class PostgresRepos:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def count_sent(self, customer_id: str, hours: int) -> int:
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=hours)
        with self.session_factory() as session:
            statement = select(ActionModel).where(
                ActionModel.customer_id == customer_id,
                ActionModel.type == "SEND_MESSAGE",
                ActionModel.created_at >= cutoff
            )
            return len(session.exec(statement).all())

    async def get_customer(self, customer_id: str) -> Optional[CustomerModel]:
        with self.session_factory() as session:
            return session.get(CustomerModel, customer_id)

    async def save_customer(self, customer: Customer) -> None:
        model = CustomerModel(**customer.model_dump())
        with self.session_factory() as session:
            session.add(model)
            session.commit()

    async def get_invoices(self, customer_id: str) -> List[InvoiceModel]:
        with self.session_factory() as session:
            statement = select(InvoiceModel).where(InvoiceModel.customer_id == customer_id)
            return list(session.exec(statement).all())

    async def save_invoice(self, invoice: Invoice) -> None:
        model = InvoiceModel(**invoice.model_dump())
        with self.session_factory() as session:
            session.add(model)
            session.commit()

    async def get_tactic_stats(self, tenant_id: str, tactic_key: Optional[str] = None) -> List[TacticStatModel]:
        with self.session_factory() as session:
            if tactic_key:
                statement = select(TacticStatModel).where(
                    TacticStatModel.tenant_id == tenant_id,
                    TacticStatModel.tactic_key == tactic_key
                )
            else:
                statement = select(TacticStatModel).where(TacticStatModel.tenant_id == tenant_id)
            return list(session.exec(statement).all())

    async def save_tactic_stat(self, stat: TacticStat) -> None:
        model = TacticStatModel(**stat.model_dump())
        with self.session_factory() as session:
            session.merge(model)
            session.commit()

class ActionRepo:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def save(self, proposal, decision, skill_name: str, tenant_id: str, customer_id: str) -> Action:
        import uuid
        import json
        now = datetime.now(timezone.utc)

        action = ActionModel(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            customer_id=customer_id,
            skill=skill_name,
            type=proposal.type,
            payload_json=json.dumps(proposal.payload),
            rationale=proposal.rationale,
            priority=proposal.priority,
            expected_value_paise=proposal.expected_value,
            status="proposed" if decision.verdict == "allow" else decision.verdict,
            dedupe_key=proposal.dedupe_key,
            not_before=decision.not_before,
            created_at=now
        )
        with self.session_factory() as session:
            session.add(action)
            session.commit()

        # Return Domain Action Model for caller
        return Action(
            id=action.id,
            tenant_id=action.tenant_id,
            customer_id=action.customer_id,
            skill=action.skill,
            type=action.type,
            payload=proposal.payload,
            rationale=action.rationale,
            evidence_memory_ids=proposal.evidence_ids,
            priority=action.priority,
            expected_value_paise=action.expected_value_paise,
            status=action.status,
            dedupe_key=action.dedupe_key,
            not_before=action.not_before,
            created_at=action.created_at
        )

    async def schedule(self, action: Action, not_before: datetime) -> None:
        with self.session_factory() as session:
            model = session.get(ActionModel, action.id)
            if model:
                model.not_before = not_before
                session.add(model)
                session.commit()
