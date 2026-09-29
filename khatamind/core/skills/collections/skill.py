import json
from typing import List
from pydantic import BaseModel
from core.skills.base import Skill, SkillContext, ActionProposal
from core.domain.events import InvoiceDueSoon, InvoiceOverdue, PromiseBroken, DayTick

class MessageDraft(BaseModel):
    message: str
    channel: str
    rationale: str
    evidence_ids: List[str]

class CollectionsSkill(Skill):
    name = "collections"
    triggers = {InvoiceDueSoon, InvoiceOverdue, PromiseBroken, DayTick}

    async def propose(self, ctx: SkillContext, event) -> List[ActionProposal]:
        if not hasattr(event, "invoice_id"):
            return [] # In MVP, we only trigger dunning on specific invoice events

        # 1. Recall memory and load playbook
        query = f"How does customer {event.customer_id} usually respond to payment reminders? What worked and what did not? Any broken promises?"
        memories = await ctx.memory.recall(event.tenant_id, query)

        playbook = await ctx.playbook.generate_playbook(event.tenant_id, event.customer_id)

        language = playbook.language.value if playbook.language else "en"
        tone = playbook.tone.value if playbook.tone else "polite"

        # 2. Choose stage (simplified for MVP: default to gentle/firm)
        # 3. LLM proposes candidate message draft
        system_prompt = f"""You draft short, respectful payment follow-ups for a small business owner in India.
Use the customer's language ({language}) and tone ({tone}). Include invoice placeholder {{invoice_no}},
amount INR {{amount}}, and the literal placeholder {{PAYMENT_LINK}}. No threats, shaming, legal
claims, or false urgency. Under 60 words."""

        user_prompt = f"Playbook: {playbook.model_dump_json()}\nRelevant past memories: {[m.text for m in memories]}"

        draft = await ctx.llm.complete_json(
            system=system_prompt,
            user=user_prompt,
            schema=MessageDraft
        )

        # 4. Selector re-ranks using the ledger (Simplified: assumes draft returned best channel)
        best_channel = await ctx.ledger.select_tactic(event.tenant_id, event.customer_id, [draft.channel, "whatsapp", "sms"])

        # 5. Emit ActionProposal
        priority = 0.5 # Simplified priority score

        proposal = ActionProposal(
            type="SEND_MESSAGE",
            payload={"text": draft.message, "channel": best_channel, "invoice_id": event.invoice_id},
            rationale=draft.rationale,
            evidence_ids=draft.evidence_ids,
            priority=priority,
            expected_value=1000,
            dedupe_key=f"dunning_{event.invoice_id}"
        )

        return [proposal]
