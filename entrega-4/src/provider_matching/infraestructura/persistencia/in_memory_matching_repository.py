from uuid import UUID

from provider_matching.dominio.entidades import Matching
from provider_matching.dominio.repositorios import MatchingRepository


class InMemoryMatchingRepository(MatchingRepository):
    def __init__(self):
        self._store: dict[UUID, Matching] = {}

    def obtener_por_id(self, id: UUID) -> Matching | None:
        return self._store.get(id)

    def agregar(self, entity: Matching):
        self._store[entity.id] = entity
