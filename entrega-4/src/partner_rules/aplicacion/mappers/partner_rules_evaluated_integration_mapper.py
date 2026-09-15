from published_language.v1.partner_rules_evaluated import PartnerRulesEvaluatedV1
from partner_rules.dominio.eventos import PartnerRulesEvaluated


class PartnerRulesEvaluatedIntegrationMapper:
    @staticmethod
    def to_integration(evento: PartnerRulesEvaluated) -> PartnerRulesEvaluatedV1:
        occurred_at = int(evento.fecha_evento.timestamp() * 1000)
        return PartnerRulesEvaluatedV1(
            event_id=str(evento.id),
            occurred_at=occurred_at,
            schema_version='1',
            partner_id=evento.partner_id or '',
            external_reference=evento.external_reference or '',
            city=evento.city or '',
            country=evento.country or '',
            service_type=evento.service_type or '',
            allowed=bool(evento.allowed),
        )
