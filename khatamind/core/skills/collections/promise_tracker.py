from typing import List
from core.skills.base import Skill, SkillContext, ActionProposal
from core.domain.events import PromiseBroken, PromiseDue

class PromiseTrackerSkill(Skill):
    name = "promise_tracker"
    triggers = {PromiseDue, PromiseBroken}

    async def propose(self, ctx: SkillContext, event) -> List[ActionProposal]:
        # Handle broken promise
        if isinstance(event, PromiseBroken):
            # Fetch playbook to get contact language and tone
            playbook = await ctx.playbook.generate_playbook(event.tenant_id, event.customer_id)
            language = playbook.language.value if playbook.language else "en"

            # Simplified proposal generation for broken promises
            proposal = ActionProposal(
                type="CREATE_TASK",
                payload={"description": f"Follow up on broken promise for promise_id: {event.promise_id}"},
                rationale="Promise was broken, immediate owner follow-up needed.",
                evidence_ids=[],
                priority=1.0,
                expected_value=0,
                dedupe_key=f"broken_promise_task_{event.promise_id}"
            )
            return [proposal]

        return []
