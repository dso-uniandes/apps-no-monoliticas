from partner_integration.aplicacion.handlers.normalize_partner_request import (
    NormalizePartnerRequestHandler,
)
from partner_integration.aplicacion.puertos.event_publisher import EventPublisher
from partner_integration.config.settings import settings
from partner_integration.dominio.repositorios import PartnerRequestRepository
from partner_integration.infraestructura.adapters.registry import get_payload_adapters
from partner_integration.infraestructura.mensajeria.noop_event_publisher import NoOpEventPublisher
from partner_integration.infraestructura.persistencia.in_memory_partner_request_repository import (
    InMemoryPartnerRequestRepository,
)

_partner_request_repository: PartnerRequestRepository | None = None
_event_publisher: EventPublisher | None = None


def _build_event_publisher() -> EventPublisher:
    if settings.MESSAGING_ENABLED:
        from partner_integration.infraestructura.mensajeria.pulsar_event_publisher import (
            PulsarEventPublisher,
        )

        listener_name = settings.PULSAR_LISTENER_NAME.strip() or None
        return PulsarEventPublisher(
            pulsar_url=settings.PULSAR_URL,
            topic=settings.EVALUATE_PARTNER_RULES_TOPIC,
            listener_name=listener_name,
        )
    return NoOpEventPublisher()


def get_partner_request_repository() -> PartnerRequestRepository:
    global _partner_request_repository
    if _partner_request_repository is None:
        if settings.PERSISTENCE_BACKEND == 'sqlite':
            from partner_integration.infraestructura.persistencia.sqlite_partner_request_repository import (
                SQLitePartnerRequestRepository,
            )

            _partner_request_repository = SQLitePartnerRequestRepository(
                settings.DATABASE_URL,
                settings.AUTO_CREATE_SCHEMA,
            )
        else:
            _partner_request_repository = InMemoryPartnerRequestRepository()
    return _partner_request_repository


def get_event_publisher() -> EventPublisher:
    global _event_publisher
    if _event_publisher is None:
        _event_publisher = _build_event_publisher()
    return _event_publisher


def get_normalize_partner_request_handler() -> NormalizePartnerRequestHandler:
    return NormalizePartnerRequestHandler(
        repositorio=get_partner_request_repository(),
        event_publisher=get_event_publisher(),
        payload_adapters=get_payload_adapters(),
    )


def shutdown_messaging() -> None:
    global _event_publisher
    if _event_publisher is not None:
        _event_publisher.close()
        _event_publisher = None


def shutdown_persistence() -> None:
    global _partner_request_repository
    _partner_request_repository = None
