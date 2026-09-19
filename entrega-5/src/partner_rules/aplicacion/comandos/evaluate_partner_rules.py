from dataclasses import dataclass

from seedwork.aplicacion.comandos import Comando


@dataclass
class EvaluatePartnerRules(Comando):
    partner_id: str
    service_type: str | None = None
    external_reference: str = ''
    city: str = ''
    country: str = ''
