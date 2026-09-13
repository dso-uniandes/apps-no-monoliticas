from abc import ABC, abstractmethod


class EventPublisher(ABC):
    @abstractmethod
    def publish(self, evento: object) -> None:
        ...

    def close(self) -> None:
        return None
