from datetime import datetime, timezone, timedelta
from core.app.ports import ClockPort

class SimulatedClock(ClockPort):
    def __init__(self, start_time: datetime):
        self._now = start_time

    def now(self) -> datetime:
        return self._now

    def advance(self, td: timedelta) -> None:
        self._now += td
