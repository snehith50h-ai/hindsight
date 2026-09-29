from datetime import datetime, timezone
import json
from core.app.ports import MemoryPort, LLMPort
from core.domain.models import Playbook

class PlaybookService:
    def __init__(self, memory: MemoryPort, llm: LLMPort):
        self.memory = memory
        self.llm = llm

    async def generate_playbook(self, tenant_id: str, customer_id: str) -> Playbook:
        # Ask memory to reflect on the customer
        query = f"Summarize how {customer_id} prefers to be contacted and paid: best channel, time, language, tone, response to discounts, real approver, reliability of promises, cautions. Be specific and cite dated evidence."
        reflection = await self.memory.reflect(tenant_id, query)

        # Use LLM to structure the reflection into a Playbook schema
        system_prompt = """Given the reflection text and the outcome statistics, produce the playbook JSON.
Only assert a field if supported by evidence; otherwise set it null and confidence 'learning'.
Fields: channel, best_hours, tone, language, incentive_response, approver, promise_reliability,
reorder_cycle_days, interests, cautions. Each field: {value, confidence, evidence_ids}."""

        playbook = await self.llm.complete_json(
            system=system_prompt,
            user=f"Reflection: {reflection}",
            schema=Playbook
        )
        playbook.customer_id = customer_id
        playbook.updated_at = datetime.now(timezone.utc)
        return playbook
