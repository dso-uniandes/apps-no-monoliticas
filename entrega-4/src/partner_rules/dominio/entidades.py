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

    def coincide_service_type(self, service_type: str) -> bool:
        return (
            self.rule_type is not None
            and self.value is not None
            and self.rule_type.valor == 'service_type'
            and self.value.valor == service_type
        )

    @staticmethod
    def filtrar_aplicables(
        reglas: list['PartnerRule'],
        partner_id: str,
        service_type: str | None = None,
    ) -> list['PartnerRule']:
        aplicables = [regla for regla in reglas if regla.aplica_a(partner_id)]
        if service_type:
            aplicables = [
                regla for regla in aplicables if regla.coincide_service_type(service_type)
            ]
        return aplicables

    @staticmethod
    def decidir_permitido(
        aplicables: list['PartnerRule'],
        service_type: str | None,
    ) -> bool:
        if service_type:
            return len(aplicables) > 0
        return True
