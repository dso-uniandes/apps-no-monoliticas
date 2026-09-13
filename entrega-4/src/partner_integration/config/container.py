from partner_integration.aplicacion.handlers.normalize_partner_request import NormalizePartnerRequestHandler
from partner_integration.config.settings import settings
from partner_integration.dominio.repositorios import PartnerRequestRepository
from partner_integration.infraestructura.adapters.registry import get_payload_adapters
from partner_integration.infraestructura.mensajeria.noop_event_publisher import NoOpEventPublisher
from partner_integration.infraestructura.persistencia.in_memory_partner_request_repository import (
    InMemoryPartnerRequestRepository,
)

_partner_request_repository: PartnerRequestRepository | None = None
_event_publisher = NoOpEventPublisher()


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


def get_normalize_partner_request_handler() -> NormalizePartnerRequestHandler:
    return NormalizePartnerRequestHandler(
        repositorio=get_partner_request_repository(),
        event_publisher=_event_publisher,
        payload_adapters=get_payload_adapters(),
    )


def shutdown_persistence() -> None:
    global _partner_request_repository
    _partner_request_repository = None
