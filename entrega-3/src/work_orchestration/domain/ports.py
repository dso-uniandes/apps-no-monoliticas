from abc import ABC, abstractmethod
from uuid import UUID
from .model import Work

class WorkRepository(ABC):
    @abstractmethod
    def add(self, work: Work) -> None: ...
    @abstractmethod
    def get(self, work_id: UUID) -> Work | None: ...

class EventPublisher(ABC):
    @abstractmethod
    def publish(self, event) -> None: ...
