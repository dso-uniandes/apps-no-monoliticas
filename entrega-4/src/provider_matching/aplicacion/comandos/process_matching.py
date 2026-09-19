from dataclasses import dataclass

from seedwork.aplicacion.comandos import Comando


@dataclass
class ProcessMatching(Comando):
    work_id: str
    candidate_provider_id: str | None = None
