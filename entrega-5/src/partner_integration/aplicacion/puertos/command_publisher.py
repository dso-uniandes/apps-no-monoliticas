from abc import ABC, abstractmethod


class CommandPublisher(ABC):
    @abstractmethod
    def publish(self, comando: object) -> None:
        ...

    def close(self) -> None:
        return None
