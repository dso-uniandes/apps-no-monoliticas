from dataclasses import dataclass
import uuid

from seedwork.dominio.eventos import EventoDominio


@dataclass
class MatchingCompleted(EventoDominio):
    matching_id: uuid.UUID | None = None
    work_id: str | None = None
    provider_id: str | None = None
    status: str | None = None
