from uuid import UUID

from partner_integration.dominio.entidades import PartnerRequest
from partner_integration.dominio.repositorios import PartnerRequestRepository


class InMemoryPartnerRequestRepository(PartnerRequestRepository):
    def __init__(self):
        self._store: dict[UUID, PartnerRequest] = {}

    def obtener_por_id(self, id: UUID) -> PartnerRequest | None:
        return self._store.get(id)

    def agregar(self, entity: PartnerRequest):
        self._store[entity.id] = entity
