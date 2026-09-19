from abc import ABC, abstractmethod
from uuid import UUID

from seedwork.dominio.repositorios import Repositorio

from .entidades import Work


class WorkRepository(Repositorio, ABC):
    @abstractmethod
    def obtener_por_id(self, id: UUID) -> Work | None:
        ...

    @abstractmethod
    def obtener_por_external_reference(self, external_reference: str) -> Work | None:
        ...

    @abstractmethod
    def agregar(self, entity: Work):
        ...

    @abstractmethod
    def actualizar(self, entity: Work) -> None:
        ...

    @abstractmethod
    def eliminar(self, id: UUID) -> bool:
        ...
