from uuid import UUID

from partner_rules.dominio.entidades import PartnerRule
from partner_rules.dominio.repositorios import PartnerRuleRepository


class InMemoryPartnerRuleRepository(PartnerRuleRepository):
    def __init__(self):
        self._store: dict[UUID, PartnerRule] = {}

    def obtener_por_id(self, id: UUID) -> PartnerRule | None:
        return self._store.get(id)

    def agregar(self, entity: PartnerRule):
        self._store[entity.id] = entity

    def obtener_por_partner(self, partner_id: str) -> list[PartnerRule]:
        return [
            regla
            for regla in self._store.values()
            if regla.partner_id is not None and regla.partner_id.valor == partner_id
        ]
