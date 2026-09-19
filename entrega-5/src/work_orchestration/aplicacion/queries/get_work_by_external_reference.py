from dataclasses import dataclass

from seedwork.aplicacion.queries import Query


@dataclass
class GetWorkByExternalReference(Query):
    external_reference: str
