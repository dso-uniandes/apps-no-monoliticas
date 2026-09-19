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

    def actualizar(self, entity: PartnerRequest) -> None:
        if entity.id not in self._store:
            raise KeyError(f'PartnerRequest {entity.id} no existe')
        self._store[entity.id] = entity

    def eliminar(self, id: UUID) -> bool:
        return self._store.pop(id, None) is not None
