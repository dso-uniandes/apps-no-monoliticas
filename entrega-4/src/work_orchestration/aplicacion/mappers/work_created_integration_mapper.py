from published_language.v1.work_created import WorkCreatedV1
from work_orchestration.dominio.eventos import WorkCreated


class WorkCreatedIntegrationMapper:
    @staticmethod
    def to_integration(evento: WorkCreated) -> WorkCreatedV1:
        occurred_at = int(evento.fecha_evento.timestamp() * 1000)
        return WorkCreatedV1(
            event_id=str(evento.id),
            occurred_at=occurred_at,
            schema_version='1',
            work_id=str(evento.work_id),
            partner_id=evento.partner_id or '',
            external_reference=evento.external_reference or '',
            status=evento.status or '',
            city=evento.city or '',
            country=evento.country or '',
        )
