from work_orchestration.aplicacion.handlers.create_work import CreateWorkHandler
from work_orchestration.aplicacion.handlers.get_work import GetWorkHandler
from work_orchestration.aplicacion.puertos.event_publisher import EventPublisher
from work_orchestration.config.settings import settings
from work_orchestration.infraestructura.mensajeria.noop_event_publisher import NoOpEventPublisher
from work_orchestration.infraestructura.persistencia.in_memory_work_repository import (
    InMemoryWorkRepository,
)

_work_repository = InMemoryWorkRepository()
_event_publisher: EventPublisher | None = None


def _build_event_publisher() -> EventPublisher:
    if settings.MESSAGING_ENABLED:
        from work_orchestration.infraestructura.mensajeria.pulsar_event_publisher import (
            PulsarEventPublisher,
        )

        return PulsarEventPublisher(
            pulsar_url=settings.PULSAR_URL,
            topic=settings.WORK_CREATED_TOPIC,
        )
    return NoOpEventPublisher()


def get_event_publisher() -> EventPublisher:
    global _event_publisher
    if _event_publisher is None:
        _event_publisher = _build_event_publisher()
    return _event_publisher


def get_create_work_handler() -> CreateWorkHandler:
    return CreateWorkHandler(
        repositorio=_work_repository,
        event_publisher=get_event_publisher(),
    )


def get_get_work_handler() -> GetWorkHandler:
    return GetWorkHandler(repositorio=_work_repository)


def shutdown_messaging() -> None:
    global _event_publisher
    if _event_publisher is not None:
        _event_publisher.close()
        _event_publisher = None
