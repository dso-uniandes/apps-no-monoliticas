from abc import ABC, abstractmethod
from uuid import UUID

from seedwork.dominio.repositorios import Repositorio

from .entidades import Matching


class MatchingRepository(Repositorio, ABC):
    @abstractmethod
    def obtener_por_id(self, id: UUID) -> Matching | None:
        ...

    @abstractmethod
    def agregar(self, entity: Matching):
        ...

    @abstractmethod
    def actualizar(self, entity: Matching) -> None:
        ...

    @abstractmethod
    def eliminar(self, id: UUID) -> bool:
        ...
