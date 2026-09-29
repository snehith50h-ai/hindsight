import random
from datetime import datetime, timedelta
from typing import List, Dict
from .archetypes import Archetype, pay_probability
from adapters.clock.simulated import SimulatedClock
from core.domain.events import DayTick

class SimCustomer:
    def __init__(self, cid: str, archetype: Archetype):
        self.id = cid
        self.archetype = archetype

class SimWorld:
    def __init__(self, seed: int, n_customers: int, days: int, archetypes: List[Archetype], start_date: datetime):
        self.seed = seed
        self.n_customers = n_customers
        self.days = days
        self.rng = random.Random(seed)
        self.clock = SimulatedClock(start_date)
        self.customers: List[SimCustomer] = [
            SimCustomer(f"c{i}", self.rng.choice(archetypes)) for i in range(n_customers)
        ]

    def step(self):
        # Advance the clock by 1 day
        self.clock.advance(timedelta(days=1))

        events = []
        for c in self.customers:
            # Emit DayTick event for each customer
            events.append(DayTick(event_id=f"tick_{self.clock.now().timestamp()}_{c.id}", tenant_id="sim-tenant", customer_id=c.id, occurred_at=self.clock.now()))
        return events

    def run(self):
        all_events = []
        for _ in range(self.days):
            all_events.extend(self.step())
        return all_events
