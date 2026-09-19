from dataclasses import dataclass
from uuid import UUID

from seedwork.aplicacion.comandos import ComandoHandler

from partner_rules.aplicacion.comandos.evaluate_partner_rules import EvaluatePartnerRules
from partner_rules.aplicacion.mappers.partner_rules_evaluated_integration_mapper import (
    PartnerRulesEvaluatedIntegrationMapper,
)
from partner_rules.aplicacion.puertos.event_publisher import EventPublisher
from partner_rules.dominio.entidades import PartnerRule
from partner_rules.dominio.eventos import PartnerRulesEvaluated
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
        aplicables = PartnerRule.filtrar_aplicables(
            reglas,
            comando.partner_id,
            comando.service_type,
        )
        ids = [regla.id for regla in aplicables]
        allowed = PartnerRule.decidir_permitido(aplicables, comando.service_type)

        if comando.service_type:
            summary = (
                f"service_type={comando.service_type} "
                f"{'permitido' if allowed else 'rechazado'} "
                f"para partner {comando.partner_id}"
            )
        else:
            summary = f'{len(ids)} regla(s) aplicables para partner {comando.partner_id}'

        evento_dominio = PartnerRulesEvaluated(
            partner_id=comando.partner_id,
            applicable_rule_ids=ids,
            evaluation_summary=summary,
            allowed=allowed,
            external_reference=comando.external_reference or '',
            city=comando.city or '',
            country=comando.country or '',
            service_type=comando.service_type or '',
        )
        self._event_publisher.publish(
            PartnerRulesEvaluatedIntegrationMapper.to_integration(evento_dominio)
        )

        return EvaluacionReglasResultado(
            partner_id=comando.partner_id,
            applicable_rule_ids=ids,
            summary=summary,
            allowed=allowed,
        )
