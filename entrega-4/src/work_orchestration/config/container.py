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
_matching_completed_consumer = None
_matching_failed_consumer = None
_saga_log = None


def _build_event_publisher() -> EventPublisher:
    if settings.MESSAGING_ENABLED:
        from work_orchestration.infraestructura.mensajeria.pulsar_event_publisher import (
            PulsarEventPublisher,
        )

        listener_name = settings.PULSAR_LISTENER_NAME.strip() or None
        return PulsarEventPublisher(
            pulsar_url=settings.PULSAR_URL,
            topic=settings.WORK_CREATED_TOPIC,
            cancelled_topic=settings.WORK_CANCELLED_TOPIC,
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


def get_saga_log():
    global _saga_log
    if _saga_log is None:
        from work_orchestration.infraestructura.saga_log import SagaLog

        _saga_log = SagaLog(settings.SAGA_LOG_DATABASE_URL)
    return _saga_log


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
            saga_log=get_saga_log(),
            listener_name=listener_name,
        )
    return _partner_rules_evaluated_consumer


def get_matching_failed_consumer():
    global _matching_failed_consumer
    if not settings.MESSAGING_ENABLED:
        return None

    if _matching_failed_consumer is None:
        from work_orchestration.infraestructura.mensajeria.matching_failed_consumer import (
            MatchingFailedConsumer,
        )

        listener_name = settings.PULSAR_LISTENER_NAME.strip() or None
        _matching_failed_consumer = MatchingFailedConsumer(
            pulsar_url=settings.PULSAR_URL,
            topic=settings.MATCHING_FAILED_TOPIC,
            subscription=settings.MATCHING_FAILED_SUBSCRIPTION,
            work_repository=get_work_repository(),
            event_publisher=get_event_publisher(),
            saga_log=get_saga_log(),
            listener_name=listener_name,
        )
    return _matching_failed_consumer


def get_matching_completed_consumer():
    global _matching_completed_consumer
    if not settings.MESSAGING_ENABLED:
        return None

    if _matching_completed_consumer is None:
        from work_orchestration.infraestructura.mensajeria.matching_completed_consumer import (
            MatchingCompletedConsumer,
        )

        listener_name = settings.PULSAR_LISTENER_NAME.strip() or None
        _matching_completed_consumer = MatchingCompletedConsumer(
            pulsar_url=settings.PULSAR_URL,
            topic=settings.MATCHING_COMPLETED_TOPIC,
            subscription=settings.MATCHING_COMPLETED_SUBSCRIPTION,
            saga_log=get_saga_log(),
            listener_name=listener_name,
        )
    return _matching_completed_consumer


def start_messaging() -> None:
    get_event_publisher()
    partner_rules_consumer = get_partner_rules_evaluated_consumer()
    if partner_rules_consumer is not None:
        partner_rules_consumer.start()
    matching_failed_consumer = get_matching_failed_consumer()
    if matching_failed_consumer is not None:
        matching_failed_consumer.start()
    matching_completed_consumer = get_matching_completed_consumer()
    if matching_completed_consumer is not None:
        matching_completed_consumer.start()


def shutdown_messaging() -> None:
    global _event_publisher, _partner_rules_evaluated_consumer
    global _matching_failed_consumer, _matching_completed_consumer
    if _partner_rules_evaluated_consumer is not None:
        _partner_rules_evaluated_consumer.stop()
        _partner_rules_evaluated_consumer = None
    if _matching_failed_consumer is not None:
        _matching_failed_consumer.stop()
        _matching_failed_consumer = None
    if _matching_completed_consumer is not None:
        _matching_completed_consumer.stop()
        _matching_completed_consumer = None
    if _event_publisher is not None:
        _event_publisher.close()
        _event_publisher = None


def shutdown_persistence() -> None:
    global _work_repository, _saga_log
    if settings.PERSISTENCE_BACKEND == 'postgres':
        from work_orchestration.infraestructura.persistencia.db import dispose_db

        dispose_db()
    _work_repository = None
    _saga_log = None
