from dataclasses import dataclass

from seedwork.aplicacion.comandos import Comando


@dataclass
class ProcessMatching(Comando):
    work_id: str
    external_reference: str = ''
    candidate_provider_id: str | None = None
