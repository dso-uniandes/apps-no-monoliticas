from dataclasses import dataclass
from datetime import datetime
import uuid

from seedwork.dominio.entidades import AgregacionRaiz

from .eventos import MatchingCompleted, MatchingFailed
from .excepciones import MatchingInvalido
from .objetos_valor import MatchingStatus, ProviderId, WorkId


@dataclass
class Matching(AgregacionRaiz):
    work_id: WorkId | None = None
    status: MatchingStatus | None = None
    provider_id: ProviderId | None = None

    @classmethod
    def crear(cls, work_id: str) -> 'Matching':
        if not work_id:
            raise MatchingInvalido('work_id es obligatorio')

        return cls(
            id=uuid.uuid4(),
            work_id=WorkId(work_id),
            status=MatchingStatus.pending(),
            provider_id=None,
            fecha_creacion=datetime.utcnow(),
            fecha_actualizacion=datetime.utcnow(),
        )

    def completar(self, provider_id: str, external_reference: str = '') -> None:
        if not provider_id:
            raise MatchingInvalido('provider_id es obligatorio para completar el matching')
        if self.work_id is None:
            raise MatchingInvalido('No se puede completar un matching sin work_id')

        self.provider_id = ProviderId(provider_id)
        self.status = MatchingStatus.completed()
        self.fecha_actualizacion = datetime.utcnow()
        self.agregar_evento(
            MatchingCompleted(
                matching_id=self.id,
                work_id=self.work_id.valor,
                provider_id=provider_id,
                external_reference=external_reference,
                status=self.status.valor,
            )
        )

    def fallar(self, reason: str, external_reference: str = '') -> None:
        if not reason:
            raise MatchingInvalido('reason es obligatorio para fallar el matching')
        if self.work_id is None:
            raise MatchingInvalido('No se puede fallar un matching sin work_id')

        self.status = MatchingStatus.failed()
        self.fecha_actualizacion = datetime.utcnow()
        self.agregar_evento(
            MatchingFailed(
                matching_id=self.id,
                work_id=self.work_id.valor,
                external_reference=external_reference,
                reason=reason,
                status=self.status.valor,
            )
        )
