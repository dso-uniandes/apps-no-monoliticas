from partner_rules.aplicacion.handlers.evaluate_partner_rules import EvaluatePartnerRulesHandler
from partner_rules.infraestructura.mensajeria.noop_event_publisher import NoOpEventPublisher
from partner_rules.infraestructura.persistencia.in_memory_partner_rule_repository import (
    InMemoryPartnerRuleRepository,
)

_partner_rule_repository = InMemoryPartnerRuleRepository()
_event_publisher = NoOpEventPublisher()


def get_evaluate_partner_rules_handler() -> EvaluatePartnerRulesHandler:
    return EvaluatePartnerRulesHandler(
        repositorio=_partner_rule_repository,
        event_publisher=_event_publisher,
    )
