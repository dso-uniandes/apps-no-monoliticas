from provider_matching.aplicacion.handlers.process_matching import ProcessMatchingHandler
from provider_matching.config.settings import settings
from provider_matching.dominio.repositorios import MatchingRepository
from provider_matching.infraestructura.mensajeria.noop_event_publisher import NoOpEventPublisher
from provider_matching.infraestructura.persistencia.in_memory_matching_repository import (
    InMemoryMatchingRepository,
)

_matching_repository: MatchingRepository | None = None
_event_publisher = NoOpEventPublisher()
_work_created_consumer = None


def get_matching_repository() -> MatchingRepository:
    global _matching_repository
    if _matching_repository is None:
        if settings.PERSISTENCE_BACKEND == 'sqlite':
            from provider_matching.infraestructura.persistencia.sqlite_matching_repository import (
                SQLiteMatchingRepository,
            )

            _matching_repository = SQLiteMatchingRepository(
                settings.DATABASE_URL,
                settings.AUTO_CREATE_SCHEMA,
            )
        else:
            _matching_repository = InMemoryMatchingRepository()
    return _matching_repository


def get_process_matching_handler() -> ProcessMatchingHandler:
    return ProcessMatchingHandler(
        repositorio=get_matching_repository(),
        event_publisher=_event_publisher,
    )


def get_work_created_consumer():
    global _work_created_consumer
    if not settings.MESSAGING_ENABLED:
        return None

    if _work_created_consumer is None:
        from provider_matching.infraestructura.mensajeria.work_created_consumer import (
            WorkCreatedConsumer,
        )

        listener_name = settings.PULSAR_LISTENER_NAME.strip() or None
        _work_created_consumer = WorkCreatedConsumer(
            pulsar_url=settings.PULSAR_URL,
            topic=settings.WORK_CREATED_TOPIC,
            subscription=settings.WORK_CREATED_SUBSCRIPTION,
            process_matching_handler=get_process_matching_handler(),
            listener_name=listener_name,
        )
    return _work_created_consumer


def start_messaging() -> None:
    consumer = get_work_created_consumer()
    if consumer is not None:
        consumer.start()


def shutdown_messaging() -> None:
    global _work_created_consumer
    if _work_created_consumer is not None:
        _work_created_consumer.stop()
        _work_created_consumer = None


def shutdown_persistence() -> None:
    global _matching_repository
    _matching_repository = None
