from dataclasses import dataclass
from typing import Any
from core.domain.models import Action

@dataclass
class PolicyDecision:
    verdict: str
    reasons: list[str]
    not_before: Any = None

class Deps:
    def __init__(self, registry, agent_center, context_factory, policy, actions_repo, executor, notifier):
        self.registry = registry
        self.agent_center = agent_center
        self.context_factory = context_factory
        self.policy = policy
        self.actions = actions_repo
        self.executor = executor
        self.notifier = notifier

    async def context_for(self, event):
        return await self.context_factory(event)

async def handle_event(event, deps: Deps):
    for skill in deps.registry.for_event(event):
        if not await deps.agent_center.enabled(skill.name, event.tenant_id, event.customer_id):
            continue
        ctx = await deps.context_for(event)
        proposals = await skill.propose(ctx, event)
        for p in proposals:
            decision = await deps.policy.evaluate(p, ctx)
            action = await deps.actions.save(p, decision, skill.name, event.tenant_id, event.customer_id)
            match decision.verdict:
                case "allow":
                    await deps.executor.execute(action)
                case "delay":
                    await deps.actions.schedule(action, decision.not_before)
                case "approval":
                    await deps.notifier.request_approval(action)
                case "deny":
                    pass
