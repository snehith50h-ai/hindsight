from datetime import time, timedelta
from zoneinfo import ZoneInfo
from typing import Optional
from core.app.pipeline import PolicyDecision

class ContactWindowRule:
    def __init__(self, start: time = time(9, 0), end: time = time(19, 30)):
        self.start = start
        self.end = end

    def check(self, p, ctx) -> Optional[PolicyDecision]:
        if p.type != "SEND_MESSAGE":
            return None
        local = ctx.clock.now().astimezone(ZoneInfo(ctx.tenant.timezone))
        if self.start <= local.time() <= self.end:
            return None
        nxt = local.replace(hour=self.start.hour, minute=self.start.minute, second=0, microsecond=0)
        if local.time() > self.end:
            nxt += timedelta(days=1)
        return PolicyDecision("delay", ["Outside contact window"], not_before=nxt)

class FrequencyCapRule:
    def __init__(self, per_day: int = 1, per_week: int = 3):
        self.per_day = per_day
        self.per_week = per_week

    def check(self, p, ctx) -> Optional[PolicyDecision]:
        if p.type != "SEND_MESSAGE":
            return None
        sent_day = ctx.repos.count_sent(ctx.customer.id, hours=24)
        sent_week = ctx.repos.count_sent(ctx.customer.id, hours=24 * 7)
        if sent_day >= self.per_day or sent_week >= self.per_week:
            return PolicyDecision("deny", ["Frequency cap reached"])
        return None

class PolicyEngine:
    def __init__(self, rules):
        self.rules = rules

    async def evaluate(self, p, ctx) -> PolicyDecision:
        for rule in self.rules:
            res = rule.check(p, ctx)
            if res:
                return res
        return PolicyDecision("allow", [])
