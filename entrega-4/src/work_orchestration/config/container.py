from work_orchestration.aplicacion.handlers.create_work import CreateWorkHandler
from work_orchestration.aplicacion.handlers.get_work import GetWorkHandler
from work_orchestration.infraestructura.mensajeria.noop_event_publisher import NoOpEventPublisher
from work_orchestration.infraestructura.persistencia.in_memory_work_repository import (
    InMemoryWorkRepository,
)

_work_repository = InMemoryWorkRepository()
_event_publisher = NoOpEventPublisher()


def get_create_work_handler() -> CreateWorkHandler:
    return CreateWorkHandler(
        repositorio=_work_repository,
        event_publisher=_event_publisher,
    )


def get_get_work_handler() -> GetWorkHandler:
    return GetWorkHandler(repositorio=_work_repository)
