from datetime import datetime
from typing import Sequence
from core.app.ports import MemoryPort, MemoryItem

class NullMemory(MemoryPort):
    async def retain(self, tenant_id: str, content: str, *, context: str, tags: Sequence[str] = (), timestamp: datetime | None = None, document_id: str | None = None) -> None:
        pass

    async def recall(self, tenant_id: str, query: str, *, tags: Sequence[str] = (), limit: int = 10) -> list[MemoryItem]:
        return []

    async def reflect(self, tenant_id: str, query: str, *, context: str | None = None) -> str:
        return "Not enough data to reflect (Memory OFF)."
