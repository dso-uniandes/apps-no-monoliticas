import asyncio

from partner_rules.aplicacion.comandos.evaluate_partner_rules import EvaluatePartnerRules
from partner_rules.config import container
from partner_rules.main import app
from published_language.v1.partner_rules_evaluated import PartnerRulesEvaluatedV1


def test_sqlite_seed_and_evaluation_survive_restart(tmp_path, monkeypatch):
    monkeypatch.setattr(container.settings, 'PERSISTENCE_BACKEND', 'sqlite')
    monkeypatch.setattr(container.settings, 'DATABASE_URL', f'sqlite:///{tmp_path}/rules.db')
    monkeypatch.setattr(container.settings, 'MESSAGING_ENABLED', False)
    monkeypatch.setattr(container, '_partner_rule_repository', None)
    monkeypatch.setattr(container, '_seeded', False)
    monkeypatch.setattr(container, '_event_publisher', None)
    events = []
    saved_ids = []

    async def exercise():
        for _ in range(2):
            async with app.router.lifespan_context(app):
                repository = container.get_partner_rule_repository()
                rules = repository.obtener_por_partner('partner-demo')
                assert len(rules) == 1
                saved_ids.append(rules[0].id)
                monkeypatch.setattr(container.get_event_publisher(), 'publish', events.append)
                handler = container.get_evaluate_partner_rules_handler()
                for service_type, expected in [('HOME_REPAIR', True), ('OTHER', False)]:
                    result = handler.handle(EvaluatePartnerRules(
                        partner_id='partner-demo', external_reference='request-1',
                        city='Bogota', country='CO', service_type=service_type,
                    ))
                    assert result.allowed is expected
                    assert isinstance(events[-1], PartnerRulesEvaluatedV1)
                    assert events[-1].allowed is expected
                    assert events[-1].external_reference == 'request-1'
            assert container._partner_rule_repository is None
            assert container._event_publisher is None

    asyncio.run(exercise())
    assert saved_ids[0] == saved_ids[1]
    assert len(events) == 4
