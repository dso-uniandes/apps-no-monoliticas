from dataclasses import dataclass
import uuid

from seedwork.dominio.eventos import EventoDominio


@dataclass
class WorkCreated(EventoDominio):
    work_id: uuid.UUID | None = None
    partner_id: str | None = None
    external_reference: str | None = None
    status: str | None = None
