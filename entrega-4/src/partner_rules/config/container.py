from partner_rules.aplicacion.handlers.evaluate_partner_rules import EvaluatePartnerRulesHandler
from partner_rules.aplicacion.puertos.event_publisher import EventPublisher
from partner_rules.config.settings import settings
from partner_rules.dominio.entidades import PartnerRule
from partner_rules.infraestructura.mensajeria.noop_event_publisher import NoOpEventPublisher
from partner_rules.infraestructura.persistencia.in_memory_partner_rule_repository import (
    InMemoryPartnerRuleRepository,
)

_partner_rule_repository = InMemoryPartnerRuleRepository()
_event_publisher: EventPublisher | None = None
_evaluate_partner_rules_consumer = None
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


def _build_event_publisher() -> EventPublisher:
    if settings.MESSAGING_ENABLED:
        from partner_rules.infraestructura.mensajeria.pulsar_event_publisher import (
            PulsarEventPublisher,
        )

        listener_name = settings.PULSAR_LISTENER_NAME.strip() or None
        return PulsarEventPublisher(
            pulsar_url=settings.PULSAR_URL,
            topic=settings.PARTNER_RULES_EVALUATED_TOPIC,
            listener_name=listener_name,
        )
    return NoOpEventPublisher()


def get_partner_rule_repository() -> InMemoryPartnerRuleRepository:
    _ensure_seed_rules()
    return _partner_rule_repository


def get_event_publisher() -> EventPublisher:
    global _event_publisher
    if _event_publisher is None:
        _event_publisher = _build_event_publisher()
    return _event_publisher


def get_evaluate_partner_rules_handler() -> EvaluatePartnerRulesHandler:
    return EvaluatePartnerRulesHandler(
        repositorio=get_partner_rule_repository(),
        event_publisher=get_event_publisher(),
    )


def get_evaluate_partner_rules_consumer():
    global _evaluate_partner_rules_consumer
    if not settings.MESSAGING_ENABLED:
        return None

    if _evaluate_partner_rules_consumer is None:
        from partner_rules.infraestructura.mensajeria.evaluate_partner_rules_consumer import (
            EvaluatePartnerRulesConsumer,
        )

        listener_name = settings.PULSAR_LISTENER_NAME.strip() or None
        _evaluate_partner_rules_consumer = EvaluatePartnerRulesConsumer(
            pulsar_url=settings.PULSAR_URL,
            topic=settings.EVALUATE_PARTNER_RULES_TOPIC,
            subscription=settings.EVALUATE_PARTNER_RULES_SUBSCRIPTION,
            evaluate_handler=get_evaluate_partner_rules_handler(),
            listener_name=listener_name,
        )
    return _evaluate_partner_rules_consumer


def start_messaging() -> None:
    get_event_publisher()
    consumer = get_evaluate_partner_rules_consumer()
    if consumer is not None:
        consumer.start()


def shutdown_messaging() -> None:
    global _event_publisher, _evaluate_partner_rules_consumer
    if _evaluate_partner_rules_consumer is not None:
        _evaluate_partner_rules_consumer.stop()
        _evaluate_partner_rules_consumer = None
    if _event_publisher is not None:
        _event_publisher.close()
        _event_publisher = None
