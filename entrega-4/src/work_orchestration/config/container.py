from work_orchestration.aplicacion.handlers.create_work import CreateWorkHandler
from work_orchestration.aplicacion.handlers.get_work import GetWorkHandler
from work_orchestration.aplicacion.puertos.event_publisher import EventPublisher
from work_orchestration.config.settings import settings
from work_orchestration.dominio.repositorios import WorkRepository
from work_orchestration.infraestructura.mensajeria.noop_event_publisher import NoOpEventPublisher
from work_orchestration.infraestructura.persistencia.in_memory_work_repository import (
    InMemoryWorkRepository,
)

_work_repository: WorkRepository | None = None
_event_publisher: EventPublisher | None = None
_partner_rules_evaluated_consumer = None


def _build_event_publisher() -> EventPublisher:
    if settings.MESSAGING_ENABLED:
        from work_orchestration.infraestructura.mensajeria.pulsar_event_publisher import (
            PulsarEventPublisher,
        )

        listener_name = settings.PULSAR_LISTENER_NAME.strip() or None
        return PulsarEventPublisher(
            pulsar_url=settings.PULSAR_URL,
            topic=settings.WORK_CREATED_TOPIC,
            listener_name=listener_name,
        )
    return NoOpEventPublisher()


def _build_work_repository() -> WorkRepository:
    if settings.PERSISTENCE_BACKEND == 'postgres':
        from work_orchestration.infraestructura.persistencia.db import (
            get_session_factory,
            init_db,
        )
        from work_orchestration.infraestructura.persistencia.repositorios import (
            SQLAlchemyWorkRepository,
        )

        init_db(
            database_url=settings.DATABASE_URL,
            auto_create_schema=settings.AUTO_CREATE_SCHEMA,
        )
        return SQLAlchemyWorkRepository(session_factory=get_session_factory())

    return InMemoryWorkRepository()


def get_event_publisher() -> EventPublisher:
    global _event_publisher
    if _event_publisher is None:
        _event_publisher = _build_event_publisher()
    return _event_publisher


def get_work_repository() -> WorkRepository:
    global _work_repository
    if _work_repository is None:
        _work_repository = _build_work_repository()
    return _work_repository


def get_create_work_handler() -> CreateWorkHandler:
    return CreateWorkHandler(
        repositorio=get_work_repository(),
        event_publisher=get_event_publisher(),
    )


def get_get_work_handler() -> GetWorkHandler:
    return GetWorkHandler(repositorio=get_work_repository())


def get_partner_rules_evaluated_consumer():
    global _partner_rules_evaluated_consumer
    if not settings.MESSAGING_ENABLED:
        return None

    if _partner_rules_evaluated_consumer is None:
        from work_orchestration.infraestructura.mensajeria.partner_rules_evaluated_consumer import (
            PartnerRulesEvaluatedConsumer,
        )

        listener_name = settings.PULSAR_LISTENER_NAME.strip() or None
        _partner_rules_evaluated_consumer = PartnerRulesEvaluatedConsumer(
            pulsar_url=settings.PULSAR_URL,
            topic=settings.PARTNER_RULES_EVALUATED_TOPIC,
            subscription=settings.PARTNER_RULES_EVALUATED_SUBSCRIPTION,
            create_work_handler=get_create_work_handler(),
            listener_name=listener_name,
        )
    return _partner_rules_evaluated_consumer


def start_messaging() -> None:
    get_event_publisher()
    consumer = get_partner_rules_evaluated_consumer()
    if consumer is not None:
        consumer.start()


def shutdown_messaging() -> None:
    global _event_publisher, _partner_rules_evaluated_consumer
    if _partner_rules_evaluated_consumer is not None:
        _partner_rules_evaluated_consumer.stop()
        _partner_rules_evaluated_consumer = None
    if _event_publisher is not None:
        _event_publisher.close()
        _event_publisher = None


def shutdown_persistence() -> None:
    global _work_repository
    if settings.PERSISTENCE_BACKEND == 'postgres':
        from work_orchestration.infraestructura.persistencia.db import dispose_db

        dispose_db()
    _work_repository = None
