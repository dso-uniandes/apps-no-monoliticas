from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from work_orchestration.aplicacion.comandos.create_work import CreateWork
from work_orchestration.aplicacion.handlers.create_work import CreateWorkHandler
from work_orchestration.aplicacion.handlers.get_work import GetWorkHandler
from work_orchestration.aplicacion.queries.get_work import GetWork
from work_orchestration.config.container import get_create_work_handler, get_get_work_handler
from work_orchestration.dominio.excepciones import WorkInvalido, WorkNoEncontrado

router = APIRouter()


class LocationRequest(BaseModel):
    city: str
    country: str


class CreateWorkRequest(BaseModel):
    partner_id: str
    external_reference: str
    location: LocationRequest


class WorkResponse(BaseModel):
    id: UUID
    partner_id: str
    external_reference: str
    status: str
    location: LocationRequest
    created_at: str


def _to_response(work) -> WorkResponse:
    return WorkResponse(
        id=work.id,
        partner_id=work.partner_id.valor,
        external_reference=work.external_reference.valor,
        status=work.status.valor,
        location=LocationRequest(
            city=work.location.city,
            country=work.location.country,
        ),
        created_at=work.fecha_creacion.isoformat(),
    )


@router.post('/works', status_code=status.HTTP_201_CREATED, response_model=WorkResponse)
def create_work(
    request: CreateWorkRequest,
    handler: CreateWorkHandler = Depends(get_create_work_handler),
) -> WorkResponse:
    comando = CreateWork(
        partner_id=request.partner_id,
        external_reference=request.external_reference,
        city=request.location.city,
        country=request.location.country,
    )
    try:
        work = handler.handle(comando)
    except WorkInvalido as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _to_response(work)


@router.get('/works/{work_id}', response_model=WorkResponse)
def get_work(
    work_id: UUID,
    handler: GetWorkHandler = Depends(get_get_work_handler),
) -> WorkResponse:
    query = GetWork(work_id=work_id)
    try:
        resultado = handler.handle(query)
    except WorkNoEncontrado as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _to_response(resultado.resultado)
