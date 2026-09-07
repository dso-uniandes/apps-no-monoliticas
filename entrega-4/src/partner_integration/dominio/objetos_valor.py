from dataclasses import dataclass
from seedwork.dominio.objetos_valor import ObjetoValor


@dataclass(frozen=True)
class PartnerId(ObjetoValor):
    valor: str


@dataclass(frozen=True)
class ExternalReference(ObjetoValor):
    valor: str
