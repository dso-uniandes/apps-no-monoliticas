from datetime import datetime

from provider_matching.aplicacion.comandos.process_matching import ProcessMatching
from provider_matching.aplicacion.puertos.event_publisher import EventPublisher
from provider_matching.dominio.entidades import Matching
from provider_matching.dominio.eventos import MatchingCompleted, MatchingFailed
from provider_matching.dominio.repositorios import MatchingRepository
from published_language.v1.matching_completed import MatchingCompletedV1
from published_language.v1.matching_failed import MatchingFailedV1
from seedwork.aplicacion.comandos import ComandoHandler


class ProcessMatchingHandler(ComandoHandler):
    def __init__(
        self,
        repositorio: MatchingRepository,
        event_publisher: EventPublisher,
    ):
        self._repositorio = repositorio
        self._event_publisher = event_publisher

    def handle(self, comando: ProcessMatching) -> Matching:
        matching = Matching.crear(work_id=comando.work_id)

        if 'fail' in (comando.external_reference or '').lower():
            matching.fallar(
                reason='No hay proveedor disponible para esta solicitud',
                external_reference=comando.external_reference,
            )
        else:
            # Logica minima: asigna un provider recibido por contrato o un placeholder.
            provider_id = comando.candidate_provider_id or 'provider-pending'
            matching.completar(provider_id, external_reference=comando.external_reference)

        self._repositorio.agregar(matching)

        for evento in matching.eventos:
            self._event_publisher.publish(self._to_integration_event(evento))
        matching.limpiar_eventos()

        return matching

    def _to_integration_event(self, evento):
        occurred_at = int(datetime.utcnow().timestamp() * 1000)
        if isinstance(evento, MatchingCompleted):
            return MatchingCompletedV1(
                event_id=str(evento.id),
                occurred_at=occurred_at,
                schema_version='1',
                matching_id=str(evento.matching_id),
                work_id=evento.work_id or '',
                external_reference=evento.external_reference or '',
                provider_id=evento.provider_id or '',
                status=evento.status or '',
            )

        if isinstance(evento, MatchingFailed):
            return MatchingFailedV1(
                event_id=str(evento.id),
                occurred_at=occurred_at,
                schema_version='1',
                matching_id=str(evento.matching_id),
                work_id=evento.work_id or '',
                external_reference=evento.external_reference or '',
                reason=evento.reason or '',
                status=evento.status or '',
            )

        return evento
