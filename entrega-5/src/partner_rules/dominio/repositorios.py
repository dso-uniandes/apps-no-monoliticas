from abc import ABC, abstractmethod
from uuid import UUID

from seedwork.dominio.repositorios import Repositorio

from .entidades import PartnerRule


class PartnerRuleRepository(Repositorio, ABC):
    @abstractmethod
    def obtener_por_id(self, id: UUID) -> PartnerRule | None:
        ...

    @abstractmethod
    def agregar(self, entity: PartnerRule):
        ...

    @abstractmethod
    def actualizar(self, entity: PartnerRule) -> None:
        ...

    @abstractmethod
    def eliminar(self, id: UUID) -> bool:
        ...

    @abstractmethod
    def obtener_por_partner(self, partner_id: str) -> list[PartnerRule]:
        ...
