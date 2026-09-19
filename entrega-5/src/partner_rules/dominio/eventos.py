from dataclasses import dataclass, field
import uuid

from seedwork.dominio.eventos import EventoDominio


@dataclass
class PartnerRulesEvaluated(EventoDominio):
    partner_id: str | None = None
    applicable_rule_ids: list[uuid.UUID] = field(default_factory=list)
    evaluation_summary: str | None = None
    allowed: bool = True
    external_reference: str | None = None
    city: str | None = None
    country: str | None = None
    service_type: str | None = None
