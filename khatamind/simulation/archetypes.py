from dataclasses import dataclass, field
import random

@dataclass(frozen=True)
class Archetype:
    name: str
    base_delay_days: int
    promise_keep_rate: float
    pays_after_call_only: bool = False
    discount_elasticity: float = 0.0
    channel_mult: dict = field(default_factory=lambda: {"whatsapp": 1.0, "call": 1.0, "sms": 0.8})
    language_mult: dict = field(default_factory=lambda: {"en": 1.0})
    overcontact_churn_hazard: float = 0.0
    dispute_rate: float = 0.0

def pay_probability(arch: Archetype, action, rng: random.Random) -> float:
    p = 0.25
    p *= arch.channel_mult.get(action.channel, 1.0) if hasattr(action, "channel") else 1.0
    p *= arch.language_mult.get(action.language, 1.0) if hasattr(action, "language") else 1.0
    if arch.pays_after_call_only and (not hasattr(action, "channel") or action.channel != "call"):
        p *= 0.3
    p += arch.discount_elasticity * getattr(action, "discount_pct", 0.0)
    return max(0.0, min(0.95, p))

# Standard archetypes
CHRONIC_PROMISER = Archetype(
    name="Chronic Promiser", base_delay_days=15, promise_keep_rate=0.4, pays_after_call_only=True
)
DEAL_SEEKER = Archetype(
    name="Deal Seeker", base_delay_days=10, promise_keep_rate=0.8, discount_elasticity=0.05
)
SILENT_PAYER = Archetype(
    name="Silent Payer", base_delay_days=12, promise_keep_rate=0.9, overcontact_churn_hazard=0.1
)
LOYAL_FAST_PAYER = Archetype(
    name="Loyal Fast Payer", base_delay_days=2, promise_keep_rate=0.95
)
