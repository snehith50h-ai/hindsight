import asyncio
from typing import Sequence, Optional
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential
from hindsight_client import Hindsight
from core.app.ports import MemoryPort, MemoryItem

class HindsightMemory(MemoryPort):
    def __init__(self, base_url: str, api_key: str | None = None, bank_prefix: str = "msme-"):
        self._client = Hindsight(base_url=base_url)
        self._prefix = bank_prefix

    def _bank(self, tenant_id: str) -> str:
        return f"{self._prefix}{tenant_id}"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
    async def retain(self, tenant_id: str, content: str, *, context: str, tags: Sequence[str] = (), timestamp: datetime | None = None, document_id: str | None = None) -> None:
        kwargs = dict(bank_id=self._bank(tenant_id), content=content, context=context)
        if timestamp:
            kwargs["timestamp"] = timestamp.isoformat()
        if tags:
            kwargs["tags"] = list(tags)
        if document_id:
            kwargs["document_id"] = document_id

        await asyncio.to_thread(self._client.retain, **kwargs)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
    async def recall(self, tenant_id: str, query: str, *, tags: Sequence[str] = (), limit: int = 10) -> list[MemoryItem]:
        res = await asyncio.to_thread(self._client.recall, bank_id=self._bank(tenant_id), query=query)
        rows = getattr(res, "results", res)
        return [MemoryItem(id=getattr(r, "id", None), text=getattr(r, "text", str(r))) for r in rows][:limit]

    async def reflect(self, tenant_id: str, query: str, *, context: str | None = None) -> str:
        res = await asyncio.to_thread(self._client.reflect, bank_id=self._bank(tenant_id), query=query)
        return getattr(res, "text", str(res))
