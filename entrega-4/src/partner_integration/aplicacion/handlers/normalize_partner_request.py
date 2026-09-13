from seedwork.aplicacion.comandos import ComandoHandler

from partner_integration.aplicacion.comandos.normalize_partner_request import NormalizePartnerRequest
from partner_integration.aplicacion.puertos.event_publisher import EventPublisher
from partner_integration.aplicacion.puertos.payload_adapter import PartnerPayloadAdapter
from partner_integration.dominio.entidades import PartnerRequest
from partner_integration.dominio.excepciones import PartnerRequestInvalido
from partner_integration.dominio.repositorios import PartnerRequestRepository


class NormalizePartnerRequestHandler(ComandoHandler):
    def __init__(
        self,
        repositorio: PartnerRequestRepository,
        event_publisher: EventPublisher,
        payload_adapters: dict[str, PartnerPayloadAdapter] | None = None,
    ):
        self._repositorio = repositorio
        self._event_publisher = event_publisher
        self._payload_adapters = payload_adapters or {}

    def handle(self, comando: NormalizePartnerRequest) -> PartnerRequest:
        external_reference = comando.external_reference
        payload = dict(comando.payload or {})

        adapter = self._payload_adapters.get(comando.partner_id)
        if adapter is not None:
            adapted = adapter.adapt(payload)
            external_reference = adapted.external_reference
            payload = {
                key: value
                for key, value in adapted.canonical_payload.items()
                if value is not None
            }

        if not external_reference:
            raise PartnerRequestInvalido('external_reference es obligatorio')

        partner_request = PartnerRequest.crear(
            partner_id=comando.partner_id,
            external_reference=external_reference,
            payload=payload,
        )
        partner_request.normalize()
        self._repositorio.agregar(partner_request)

        for evento in partner_request.eventos:
            self._event_publisher.publish(evento)
        partner_request.limpiar_eventos()

        return partner_request
