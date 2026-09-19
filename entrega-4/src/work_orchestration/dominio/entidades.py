from dataclasses import dataclass
from datetime import datetime
import uuid

from seedwork.dominio.entidades import AgregacionRaiz

from .eventos import WorkCreated
from .excepciones import WorkInvalido
from .objetos_valor import ExternalReference, Location, PartnerId, WorkStatus


@dataclass
class Work(AgregacionRaiz):
    partner_id: PartnerId | None = None
    external_reference: ExternalReference | None = None
    status: WorkStatus | None = None
    location: Location | None = None

    @classmethod
    def create(
        cls,
        partner_id: str,
        external_reference: str,
        city: str,
        country: str,
    ) -> 'Work':
        if not partner_id or not external_reference:
            raise WorkInvalido('partner_id y external_reference son obligatorios')
        if not city or not country:
            raise WorkInvalido('location.city y location.country son obligatorios')

        status = WorkStatus.created()
        work = cls(
            id=uuid.uuid4(),
            partner_id=PartnerId(partner_id),
            external_reference=ExternalReference(external_reference),
            status=status,
            location=Location(city=city, country=country),
            fecha_creacion=datetime.utcnow(),
            fecha_actualizacion=datetime.utcnow(),
        )
        work.agregar_evento(
            WorkCreated(
                work_id=work.id,
                partner_id=partner_id,
                external_reference=external_reference,
                status=status.valor,
                city=city,
                country=country,
            )
        )
        return work

    @classmethod
    def rehydrate(
        cls,
        id: uuid.UUID,
        partner_id: str,
        external_reference: str,
        status: str,
        city: str,
        country: str,
        created_at: datetime,
    ) -> 'Work':
        """Reconstruye el agregado desde persistencia sin emitir eventos de dominio."""
        return cls(
            id=id,
            partner_id=PartnerId(partner_id),
            external_reference=ExternalReference(external_reference),
            status=WorkStatus(status),
            location=Location(city=city, country=country),
            fecha_creacion=created_at,
            fecha_actualizacion=created_at,
            eventos=[],
        )
