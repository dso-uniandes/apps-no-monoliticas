from dataclasses import dataclass

from seedwork.aplicacion.comandos import Comando


@dataclass
class EvaluatePartnerRules(Comando):
    partner_id: str
