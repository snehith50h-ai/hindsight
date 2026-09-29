from abc import ABC, abstractmethod
from typing import ClassVar, List, Type, Any
from core.domain.models import Action
from core.domain.events import DomainEvent

class ActionProposal:
    def __init__(self, type: str, payload: dict, rationale: str, evidence_ids: list[str], priority: float, expected_value: int, dedupe_key: str):
        self.type = type
        self.payload = payload
        self.rationale = rationale
        self.evidence_ids = evidence_ids
        self.priority = priority
        self.expected_value = expected_value
        self.dedupe_key = dedupe_key

class SkillContext:
    def __init__(self, tenant, customer, repos, memory, llm, clock, playbook, ledger, forecast):
        self.tenant = tenant
        self.customer = customer
        self.repos = repos
        self.memory = memory
        self.llm = llm
        self.clock = clock
        self.playbook = playbook
        self.ledger = ledger
        self.forecast = forecast

class Skill(ABC):
    name: ClassVar[str]
    triggers: ClassVar[set[Type[DomainEvent]]]

    @abstractmethod
    async def propose(self, ctx: SkillContext, event: DomainEvent) -> List[ActionProposal]:
        pass

class Registry:
    def __init__(self) -> None:
        self._skills: List[Skill] = []

    def register(self, skill: Skill) -> None:
        self._skills.append(skill)

    def for_event(self, event: DomainEvent) -> List[Skill]:
        return [s for s in self._skills if type(event) in s.triggers]
