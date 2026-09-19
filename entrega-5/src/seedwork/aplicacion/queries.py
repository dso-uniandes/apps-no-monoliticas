from abc import ABC, abstractmethod
from dataclasses import dataclass


class Query(ABC):
    ...


@dataclass
class ResultadoQuery:
    resultado: object | None = None


class QueryHandler(ABC):
    @abstractmethod
    def handle(self, query: Query) -> ResultadoQuery:
        raise NotImplementedError()
