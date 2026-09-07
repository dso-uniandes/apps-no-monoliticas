from dataclasses import dataclass
from uuid import UUID

from seedwork.aplicacion.queries import Query


@dataclass
class GetWork(Query):
    work_id: UUID
