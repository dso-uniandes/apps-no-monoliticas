from seedwork.aplicacion.comandos import ComandoHandler

from partner_integration.aplicacion.comandos.normalize_partner_request import NormalizePartnerRequest
from partner_integration.aplicacion.puertos.event_publisher import EventPublisher
from partner_integration.dominio.entidades import PartnerRequest
from partner_integration.dominio.repositorios import PartnerRequestRepository


class NormalizePartnerRequestHandler(ComandoHandler):
    def __init__(
        self,
        repositorio: PartnerRequestRepository,
        event_publisher: EventPublisher,
    ):
        self._repositorio = repositorio
        self._event_publisher = event_publisher

    def handle(self, comando: NormalizePartnerRequest) -> PartnerRequest:
        partner_request = PartnerRequest.crear(
            partner_id=comando.partner_id,
            external_reference=comando.external_reference,
            payload=comando.payload,
        )
        partner_request.normalize()
        self._repositorio.agregar(partner_request)

        for evento in partner_request.eventos:
            self._event_publisher.publish(evento)
        partner_request.limpiar_eventos()

        return partner_request
