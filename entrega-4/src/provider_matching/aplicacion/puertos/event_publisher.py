from abc import ABC, abstractmethod

from seedwork.dominio.eventos import EventoDominio


class EventPublisher(ABC):
    @abstractmethod
    def publish(self, evento: EventoDominio) -> None:
        ...
