from dataclasses import dataclass
from uuid import UUID

from seedwork.aplicacion.comandos import ComandoHandler

from partner_rules.aplicacion.comandos.evaluate_partner_rules import EvaluatePartnerRules
from partner_rules.aplicacion.puertos.event_publisher import EventPublisher
from partner_rules.dominio.eventos import PartnerRulesEvaluated
from partner_rules.dominio.repositorios import PartnerRuleRepository


@dataclass
class EvaluacionReglasResultado:
    partner_id: str
    applicable_rule_ids: list[UUID]
    summary: str


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
        ids = [regla.id for regla in aplicables]
        summary = f'{len(ids)} regla(s) aplicables para partner {comando.partner_id}'

        evento = PartnerRulesEvaluated(
            partner_id=comando.partner_id,
            applicable_rule_ids=ids,
            evaluation_summary=summary,
        )
        self._event_publisher.publish(evento)

        return EvaluacionReglasResultado(
            partner_id=comando.partner_id,
            applicable_rule_ids=ids,
            summary=summary,
        )
