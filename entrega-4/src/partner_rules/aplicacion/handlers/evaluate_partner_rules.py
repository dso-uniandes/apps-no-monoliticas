from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from seedwork.aplicacion.comandos import ComandoHandler

from published_language.v1.partner_rules_evaluated import PartnerRulesEvaluatedV1
from partner_rules.aplicacion.comandos.evaluate_partner_rules import EvaluatePartnerRules
from partner_rules.aplicacion.puertos.event_publisher import EventPublisher
from partner_rules.dominio.repositorios import PartnerRuleRepository


@dataclass
class EvaluacionReglasResultado:
    partner_id: str
    applicable_rule_ids: list[UUID]
    summary: str
    allowed: bool = True


class EvaluatePartnerRulesHandler(ComandoHandler):
    def __init__(
        self,
        repositorio: PartnerRuleRepository,
        event_publisher: EventPublisher,
    ):
        self._repositorio = repositorio
        self._event_publisher = event_publisher

    def handle(self, comando: EvaluatePartnerRules) -> EvaluacionReglasResultado:
        reglas = self._repositorio.obtener_por_partner(comando.partner_id)
        aplicables = [regla for regla in reglas if regla.aplica_a(comando.partner_id)]

        if comando.service_type:
            aplicables = [
                regla
                for regla in aplicables
                if regla.rule_type is not None
                and regla.value is not None
                and regla.rule_type.valor == 'service_type'
                and regla.value.valor == comando.service_type
            ]

        ids = [regla.id for regla in aplicables]
        allowed = len(ids) > 0 if comando.service_type else True
        if comando.service_type:
            summary = (
                f"service_type={comando.service_type} "
                f"{'permitido' if allowed else 'rechazado'} "
                f"para partner {comando.partner_id}"
            )
        else:
            summary = f'{len(ids)} regla(s) aplicables para partner {comando.partner_id}'

        integration_event = PartnerRulesEvaluatedV1(
            event_id=str(uuid4()),
            occurred_at=int(datetime.utcnow().timestamp() * 1000),
            schema_version='1',
            partner_id=comando.partner_id,
            external_reference=comando.external_reference or '',
            city=comando.city or '',
            country=comando.country or '',
            service_type=comando.service_type or '',
            allowed=allowed,
        )
        self._event_publisher.publish(integration_event)

        return EvaluacionReglasResultado(
            partner_id=comando.partner_id,
            applicable_rule_ids=ids,
            summary=summary,
            allowed=allowed,
        )
