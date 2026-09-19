from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from partner_integration.aplicacion.comandos.normalize_partner_request import (
    NormalizePartnerRequest,
)
from partner_integration.aplicacion.handlers.normalize_partner_request import (
    NormalizePartnerRequestHandler,
)
from partner_integration.config.container import get_normalize_partner_request_handler
from partner_integration.dominio.excepciones import PartnerRequestInvalido

router = APIRouter()


class PartnerRequestCreate(BaseModel):
    partner_id: str
    payload: dict = Field(default_factory=dict)


class PartnerRequestAccepted(BaseModel):
    status: str
    partner_id: str
    external_reference: str
    partner_request_id: str


@router.post(
    '/partner-requests',
    status_code=status.HTTP_202_ACCEPTED,
    response_model=PartnerRequestAccepted,
)
def create_partner_request(
    request: PartnerRequestCreate,
    handler: NormalizePartnerRequestHandler = Depends(get_normalize_partner_request_handler),
) -> PartnerRequestAccepted:
    comando = NormalizePartnerRequest(
        partner_id=request.partner_id,
        payload=request.payload,
    )
    try:
        partner_request = handler.handle(comando)
    except PartnerRequestInvalido as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return PartnerRequestAccepted(
        status='accepted',
        partner_id=partner_request.partner_id.valor if partner_request.partner_id else '',
        external_reference=(
            partner_request.external_reference.valor
            if partner_request.external_reference
            else ''
        ),
        partner_request_id=str(partner_request.id),
    )
