from partner_rules.aplicacion.handlers.evaluate_partner_rules import EvaluatePartnerRulesHandler
from partner_rules.dominio.entidades import PartnerRule
from partner_rules.infraestructura.mensajeria.noop_event_publisher import NoOpEventPublisher
from partner_rules.infraestructura.persistencia.in_memory_partner_rule_repository import (
    InMemoryPartnerRuleRepository,
)

_partner_rule_repository = InMemoryPartnerRuleRepository()
_event_publisher = NoOpEventPublisher()
_seeded = False


def _ensure_seed_rules() -> None:
    global _seeded
    if _seeded:
        return

    if not _partner_rule_repository.obtener_por_partner('partner-demo'):
        _partner_rule_repository.agregar(
            PartnerRule.crear(
                partner_id='partner-demo',
                rule_type='service_type',
                value='HOME_REPAIR',
                enabled=True,
            )
        )
    _seeded = True


def get_partner_rule_repository() -> InMemoryPartnerRuleRepository:
    _ensure_seed_rules()
    return _partner_rule_repository


def get_evaluate_partner_rules_handler() -> EvaluatePartnerRulesHandler:
    return EvaluatePartnerRulesHandler(
        repositorio=get_partner_rule_repository(),
        event_publisher=_event_publisher,
    )
