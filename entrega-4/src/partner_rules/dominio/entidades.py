from dataclasses import dataclass
from datetime import datetime
import uuid

from seedwork.dominio.entidades import AgregacionRaiz

from .excepciones import PartnerRuleInvalida
from .objetos_valor import PartnerId, RuleType, RuleValue


@dataclass
class PartnerRule(AgregacionRaiz):
    partner_id: PartnerId | None = None
    rule_type: RuleType | None = None
    value: RuleValue | None = None
    enabled: bool = True

    @classmethod
    def crear(
        cls,
        partner_id: str,
        rule_type: str,
        value: str,
        enabled: bool = True,
    ) -> 'PartnerRule':
        if not partner_id or not rule_type:
            raise PartnerRuleInvalida('partner_id y rule_type son obligatorios')

        return cls(
            id=uuid.uuid4(),
            partner_id=PartnerId(partner_id),
            rule_type=RuleType(rule_type),
            value=RuleValue(value),
            enabled=enabled,
            fecha_creacion=datetime.utcnow(),
            fecha_actualizacion=datetime.utcnow(),
        )

    def aplica_a(self, partner_id: str) -> bool:
        return (
            self.enabled
            and self.partner_id is not None
            and self.partner_id.valor == partner_id
        )
