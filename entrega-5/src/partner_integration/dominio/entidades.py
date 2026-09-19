from dataclasses import dataclass, field
from datetime import datetime
import uuid

from seedwork.dominio.entidades import AgregacionRaiz

from .eventos import PartnerRequestNormalized
from .excepciones import PartnerRequestInvalido
from .objetos_valor import ExternalReference, PartnerId


@dataclass
class PartnerRequest(AgregacionRaiz):
    partner_id: PartnerId | None = None
    external_reference: ExternalReference | None = None
    payload: dict = field(default_factory=dict)
    normalized_payload: dict | None = None

    @classmethod
    def crear(
        cls,
        partner_id: str,
        external_reference: str,
        payload: dict | None = None,
    ) -> 'PartnerRequest':
        if not partner_id or not external_reference:
            raise PartnerRequestInvalido('partner_id y external_reference son obligatorios')

        return cls(
            id=uuid.uuid4(),
            partner_id=PartnerId(partner_id),
            external_reference=ExternalReference(external_reference),
            payload=payload or {},
            fecha_creacion=datetime.utcnow(),
            fecha_actualizacion=datetime.utcnow(),
        )

    def normalize(self) -> None:
        if self.partner_id is None or self.external_reference is None:
            raise PartnerRequestInvalido('No se puede normalizar una solicitud incompleta')

        self.normalized_payload = {
            'partner_id': self.partner_id.valor,
            'external_reference': self.external_reference.valor,
            'data': dict(self.payload),
        }
        self.fecha_actualizacion = datetime.utcnow()
        self.agregar_evento(
            PartnerRequestNormalized(
                partner_request_id=self.id,
                partner_id=self.partner_id.valor,
                external_reference=self.external_reference.valor,
            )
        )
