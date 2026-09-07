from partner_integration.aplicacion.handlers.normalize_partner_request import NormalizePartnerRequestHandler
from partner_integration.infraestructura.mensajeria.noop_event_publisher import NoOpEventPublisher
from partner_integration.infraestructura.persistencia.in_memory_partner_request_repository import (
    InMemoryPartnerRequestRepository,
)

_partner_request_repository = InMemoryPartnerRequestRepository()
_event_publisher = NoOpEventPublisher()


def get_normalize_partner_request_handler() -> NormalizePartnerRequestHandler:
    return NormalizePartnerRequestHandler(
        repositorio=_partner_request_repository,
        event_publisher=_event_publisher,
    )
