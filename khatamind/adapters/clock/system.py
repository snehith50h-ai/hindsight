from datetime import datetime, timezone
from core.app.ports import ClockPort

class SystemClock(ClockPort):
    def now(self) -> datetime:
        return datetime.now(timezone.utc)
