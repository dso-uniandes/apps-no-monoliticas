from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

class WorkStatus(str, Enum):
    CREATED = "CREATED"
    ASSIGNED = "ASSIGNED"
    COMPLETED = "COMPLETED"

@dataclass(frozen=True)
class Location:
    city: str
    zone: str

@dataclass(frozen=True)
class WorkCreated:
    event_id: UUID
    work_id: UUID
    category: str
    city: str
    zone: str
    occurred_at: datetime

@dataclass
class Work:
    id: UUID
    category: str
    urgency: str
    location: Location
    status: WorkStatus = WorkStatus.CREATED
    _events: list = field(default_factory=list, repr=False)

    @classmethod
    def create(cls, category: str, urgency: str, location: Location):
        work = cls(uuid4(), category, urgency, location)
        work._events.append(WorkCreated(
            event_id=uuid4(), work_id=work.id, category=category,
            city=location.city, zone=location.zone,
            occurred_at=datetime.now(timezone.utc)
        ))
        return work

    def pull_events(self):
        events = list(self._events)
        self._events.clear()
        return events
