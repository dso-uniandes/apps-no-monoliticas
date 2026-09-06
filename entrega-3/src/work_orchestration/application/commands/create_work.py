from dataclasses import dataclass
from work_orchestration.domain.model import Work, Location
from work_orchestration.domain.ports import WorkRepository, EventPublisher

@dataclass(frozen=True)
class CreateWorkCommand:
    category: str
    urgency: str
    city: str
    zone: str

class CreateWorkHandler:
    def __init__(self, repository: WorkRepository, publisher: EventPublisher):
        self.repository = repository
        self.publisher = publisher

    def handle(self, command: CreateWorkCommand) -> Work:
        work = Work.create(
            command.category,
            command.urgency,
            Location(command.city, command.zone)
        )
        self.repository.add(work)
        for event in work.pull_events():
            self.publisher.publish(event)
        return work
