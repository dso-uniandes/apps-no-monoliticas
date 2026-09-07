from abc import ABC, abstractmethod
from uuid import UUID

from seedwork.dominio.repositorios import Repositorio

from .entidades import PartnerRequest


class PartnerRequestRepository(Repositorio, ABC):
    @abstractmethod
    def obtener_por_id(self, id: UUID) -> PartnerRequest | None:
        ...

    @abstractmethod
    def agregar(self, entity: PartnerRequest):
        ...
