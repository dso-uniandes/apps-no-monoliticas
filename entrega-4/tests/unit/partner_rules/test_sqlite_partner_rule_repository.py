from datetime import datetime
from uuid import uuid4

from partner_rules.dominio.entidades import PartnerRule
from partner_rules.dominio.objetos_valor import RuleValue
from partner_rules.infraestructura.persistencia.sqlite_partner_rule_repository import (
    SQLitePartnerRuleRepository,
)


def test_rule_survives_repository_reopening(tmp_path):
    url = f'sqlite:///{tmp_path}/data/rules.db'
    repository = SQLitePartnerRuleRepository(url)
    rule = PartnerRule.crear('partner-1', 'city', 'Bogotá', enabled=False)
    repository.agregar(rule)
    reopened = SQLitePartnerRuleRepository(url, auto_create_schema=False)
    restored = reopened.obtener_por_id(rule.id)
    assert restored == rule
    assert restored.enabled is False
    assert restored.eventos == []


def test_query_isolates_partners_and_includes_disabled_rules(tmp_path):
    repository = SQLitePartnerRuleRepository(f'sqlite:///{tmp_path}/rules.db')
    rules = [
        PartnerRule.crear("partner'1", 'city', 'Bogotá'),
        PartnerRule.crear("partner'1", 'sla', '24', enabled=False),
        PartnerRule.crear('partner-2', 'city', 'Medellín'),
    ]
    for rule in rules:
        repository.agregar(rule)
    found = repository.obtener_por_partner("partner'1")
    assert {rule.id for rule in found} == {rules[0].id, rules[1].id}
    assert {rule.id for rule in found if rule.aplica_a("partner'1")} == {rules[0].id}
    assert repository.obtener_por_partner("' OR 1=1 --") == []
    assert repository.obtener_por_id(uuid4()) is None


def test_saving_existing_rule_updates_without_duplicates(tmp_path):
    url = f'sqlite:///{tmp_path}/rules.db'
    repository = SQLitePartnerRuleRepository(url)
    rule = PartnerRule.crear('partner-1', 'sla', '24')
    repository.agregar(rule)
    rule.value = RuleValue('48')
    rule.enabled = False
    rule.fecha_actualizacion = datetime(2026, 9, 13, 12, 0)
    repository.agregar(rule)
    reopened = SQLitePartnerRuleRepository(url)
    assert reopened.obtener_por_id(rule.id) == rule
    assert len(reopened.obtener_por_partner('partner-1')) == 1
