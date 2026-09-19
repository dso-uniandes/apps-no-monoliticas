from uuid import UUID

from work_orchestration.dominio.entidades import Work
from work_orchestration.dominio.repositorios import WorkRepository


class InMemoryWorkRepository(WorkRepository):
    def __init__(self):
        self._store: dict[UUID, Work] = {}

    def obtener_por_id(self, id: UUID) -> Work | None:
        return self._store.get(id)

    def agregar(self, entity: Work):
        self._store[entity.id] = entity

    def actualizar(self, entity: Work) -> None:
        if entity.id not in self._store:
            raise KeyError(f'Work {entity.id} no existe')
        self._store[entity.id] = entity

    def eliminar(self, id: UUID) -> bool:
        return self._store.pop(id, None) is not None
