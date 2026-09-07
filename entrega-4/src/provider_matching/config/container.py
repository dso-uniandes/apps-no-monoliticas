from provider_matching.aplicacion.handlers.process_matching import ProcessMatchingHandler
from provider_matching.infraestructura.mensajeria.noop_event_publisher import NoOpEventPublisher
from provider_matching.infraestructura.persistencia.in_memory_matching_repository import (
    InMemoryMatchingRepository,
)

_matching_repository = InMemoryMatchingRepository()
_event_publisher = NoOpEventPublisher()


def get_process_matching_handler() -> ProcessMatchingHandler:
    return ProcessMatchingHandler(
        repositorio=_matching_repository,
        event_publisher=_event_publisher,
    )
