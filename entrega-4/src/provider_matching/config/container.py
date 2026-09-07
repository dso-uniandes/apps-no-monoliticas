from provider_matching.aplicacion.handlers.process_matching import ProcessMatchingHandler
from provider_matching.config.settings import settings
from provider_matching.infraestructura.mensajeria.noop_event_publisher import NoOpEventPublisher
from provider_matching.infraestructura.persistencia.in_memory_matching_repository import (
    InMemoryMatchingRepository,
)

_matching_repository = InMemoryMatchingRepository()
_event_publisher = NoOpEventPublisher()
_work_created_consumer = None


def get_process_matching_handler() -> ProcessMatchingHandler:
    return ProcessMatchingHandler(
        repositorio=_matching_repository,
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

        _work_created_consumer = WorkCreatedConsumer(
            pulsar_url=settings.PULSAR_URL,
            topic=settings.WORK_CREATED_TOPIC,
            subscription=settings.WORK_CREATED_SUBSCRIPTION,
            process_matching_handler=get_process_matching_handler(),
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
