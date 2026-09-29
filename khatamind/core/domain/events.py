from datetime import timezone
from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class DomainEvent(BaseModel):
    event_id: str
    tenant_id: str
    customer_id: str
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class InvoiceCreated(DomainEvent):
    invoice_id: str

class InvoiceDueSoon(DomainEvent):
    invoice_id: str

class InvoiceOverdue(DomainEvent):
    invoice_id: str

class PaymentReceived(DomainEvent):
    payment_id: str

class PartialPaymentReceived(DomainEvent):
    payment_id: str

class PromiseMade(DomainEvent):
    promise_id: str

class PromiseDue(DomainEvent):
    promise_id: str

class PromiseBroken(DomainEvent):
    promise_id: str

class PromiseKept(DomainEvent):
    promise_id: str

class CustomerReplied(DomainEvent):
    interaction_id: str
    text: str

class ComplaintRaised(DomainEvent):
    interaction_id: str
    summary: str

class DisputeRaised(DomainEvent):
    invoice_id: str
    summary: str

class DisputeResolved(DomainEvent):
    invoice_id: str
    resolution: str

class OrderPlaced(DomainEvent):
    order_id: str

class ReorderWindowOpened(DomainEvent):
    expected_order_date: datetime

class DriftDetected(DomainEvent):
    risk_score: int
    reasons: list[str]

class OwnerApproved(DomainEvent):
    action_id: str

class OwnerRejected(DomainEvent):
    action_id: str
    reason: Optional[str] = None

class OwnerEdited(DomainEvent):
    action_id: str
    original_text: str
    new_text: str
    reason: Optional[str] = None

class DayTick(DomainEvent):
    pass

class NightlyReflectionDue(DomainEvent):
    pass

class MorningBriefDue(DomainEvent):
    pass
