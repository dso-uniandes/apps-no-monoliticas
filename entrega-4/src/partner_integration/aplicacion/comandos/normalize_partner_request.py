from dataclasses import dataclass, field

from seedwork.aplicacion.comandos import Comando


@dataclass
class NormalizePartnerRequest(Comando):
    partner_id: str
    external_reference: str = ''
    payload: dict = field(default_factory=dict)
