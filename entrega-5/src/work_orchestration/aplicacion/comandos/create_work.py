from dataclasses import dataclass

from seedwork.aplicacion.comandos import Comando


@dataclass
class CreateWork(Comando):
    partner_id: str
    external_reference: str
    city: str
    country: str
