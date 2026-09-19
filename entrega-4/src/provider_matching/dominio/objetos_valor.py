from dataclasses import dataclass
from seedwork.dominio.objetos_valor import ObjetoValor


@dataclass(frozen=True)
class WorkId(ObjetoValor):
    valor: str


@dataclass(frozen=True)
class ProviderId(ObjetoValor):
    valor: str


@dataclass(frozen=True)
class MatchingStatus(ObjetoValor):
    valor: str

    @staticmethod
    def pending() -> 'MatchingStatus':
        return MatchingStatus('PENDING')

    @staticmethod
    def completed() -> 'MatchingStatus':
        return MatchingStatus('COMPLETED')
