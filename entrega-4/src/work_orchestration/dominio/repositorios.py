from abc import ABC, abstractmethod
from uuid import UUID

from seedwork.dominio.repositorios import Repositorio

from .entidades import Work


class WorkRepository(Repositorio, ABC):
    @abstractmethod
    def obtener_por_id(self, id: UUID) -> Work | None:
        ...

    @abstractmethod
    def agregar(self, entity: Work):
        ...
