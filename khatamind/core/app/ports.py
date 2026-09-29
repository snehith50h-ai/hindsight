from __future__ import annotations
from datetime import datetime
from typing import Protocol, Sequence, TypeVar, AsyncIterator, Type, Optional, Any
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class MemoryItem(BaseModel):
    id: str | None = None
    text: str
    score: float | None = None
    timestamp: datetime | None = None

class MemoryPort(Protocol):
    async def retain(self, tenant_id: str, content: str, *, context: str,
                     tags: Sequence[str] = (), timestamp: datetime | None = None,
                     document_id: str | None = None) -> None: ...
    async def recall(self, tenant_id: str, query: str, *, tags: Sequence[str] = (),
                     limit: int = 10) -> list[MemoryItem]: ...
    async def reflect(self, tenant_id: str, query: str, *, context: str | None = None) -> str: ...

class LLMPort(Protocol):
    async def complete_json(self, *, system: str, user: str, schema: Type[T],
                            temperature: float = 0.2) -> T: ...
    async def complete_text(self, *, system: str, user: str, temperature: float = 0.4) -> str: ...

class ClockPort(Protocol):
    def now(self) -> datetime: ...

class OutboundMessage(BaseModel):
    id: str
    tenant_id: str
    customer_id: str
    channel: str
    text: str

class DeliveryReceipt(BaseModel):
    message_id: str
    status: str
    timestamp: datetime

class InboundMessage(BaseModel):
    id: str
    customer_id: str
    text: str
    timestamp: datetime
    channel: str

class ChannelPort(Protocol):
    async def send(self, msg: OutboundMessage) -> DeliveryReceipt: ...
    def inbound(self) -> AsyncIterator[InboundMessage]: ...
