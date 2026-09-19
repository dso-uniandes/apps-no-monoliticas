from fastapi import APIRouter, HTTPException, Query, Response, status
from pydantic import BaseModel, Field

from bff.aplicacion.saga_status import derive_status
from bff.config.settings import settings
from bff.infraestructura.http_clients import request_upstream

router = APIRouter(prefix='/api/v1', tags=['partner-requests'])


class PartnerRequestCreate(BaseModel):
    partner_id: str
    payload: dict = Field(default_factory=dict)


class PartnerRequestAccepted(BaseModel):
    status: str
    partner_id: str
    external_reference: str
    partner_request_id: str
    status_url: str


class SagaStep(BaseModel):
    step: str
    status: str
    detail: str = ''
    created_at: str | None = None


class WorkView(BaseModel):
    id: str
    status: str
    partner_id: str
    city: str
    country: str
    created_at: str


class PartnerRequestStatus(BaseModel):
    external_reference: str
    status: str
    work: WorkView | None = None
    steps: list[SagaStep] = Field(default_factory=list)


class PartnerRequestSummary(BaseModel):
    external_reference: str
    status: str
    last_step: str = ''
    steps_count: int = 0
    updated_at: str | None = None
    status_url: str


class PartnerRequestList(BaseModel):
    total: int
    sagas: list[PartnerRequestSummary] = Field(default_factory=list)


@router.post(
    '/partner-requests',
    status_code=status.HTTP_202_ACCEPTED,
    response_model=PartnerRequestAccepted,
    summary='Registra una solicitud de partner e inicia la SAGA',
)
async def create_partner_request(request: PartnerRequestCreate) -> PartnerRequestAccepted:
    """Delega en Partner Integration (ACL) y devuelve la llave de correlacion.

    La respuesta es 202 porque la SAGA es asincrona: el `external_reference`
    y el `status_url` son el handle para consultar como avanza.
    """
    response = await request_upstream(
        'POST',
        f'{settings.PARTNER_INTEGRATION_URL}/partner-requests',
        upstream='partner-integration',
        json=request.model_dump(),
    )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=_detalle(response, 'Partner Integration rechazo la solicitud'),
        )

    body = response.json()
    external_reference = body.get('external_reference', '')
    return PartnerRequestAccepted(
        status=body.get('status', 'accepted'),
        partner_id=body.get('partner_id', ''),
        external_reference=external_reference,
        partner_request_id=body.get('partner_request_id', ''),
        status_url=f'/api/v1/partner-requests/{external_reference}',
    )


@router.get(
    '/partner-requests',
    response_model=PartnerRequestList,
    summary='Listado de las SAGAs mas recientes y su estado',
)
async def list_partner_requests(
    limit: int = Query(default=50, ge=1, le=200),
) -> PartnerRequestList:
    """Tablero de monitoreo: todas las transacciones recientes con su estado.

    El estado se deriva con la misma funcion que la consulta individual, para
    que ambas vistas no puedan contradecirse.
    """
    response = await request_upstream(
        'GET',
        f'{settings.WORK_ORCHESTRATION_URL}/sagas',
        upstream='work-orchestration',
        params={'limit': limit},
    )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=_detalle(response, 'No se pudo listar el Saga Log'),
        )

    body = response.json()
    resumenes = []
    for saga in body.get('sagas', []):
        steps = saga.get('steps', [])
        referencia = saga.get('external_reference', '')
        resumenes.append(
            PartnerRequestSummary(
                external_reference=referencia,
                status=derive_status(steps),
                last_step=steps[-1].get('step', '') if steps else '',
                steps_count=saga.get('steps_count', len(steps)),
                updated_at=saga.get('updated_at'),
                status_url=f'/api/v1/partner-requests/{referencia}',
            )
        )

    return PartnerRequestList(total=body.get('total', len(resumenes)), sagas=resumenes)


@router.get(
    '/partner-requests/{external_reference}',
    response_model=PartnerRequestStatus,
    summary='Estado consolidado de la SAGA (Work + Saga Log)',
)
async def get_partner_request_status(external_reference: str) -> PartnerRequestStatus:
    """Agrega en una sola respuesta el Saga Log y el estado del Work.

    Evita que el cliente tenga que conocer la topologia interna ni consultar
    dos endpoints distintos de Work Orchestration.
    """
    saga_response = await request_upstream(
        'GET',
        f'{settings.WORK_ORCHESTRATION_URL}/sagas/{external_reference}',
        upstream='work-orchestration',
    )

    if saga_response.status_code >= 400:
        raise HTTPException(
            status_code=saga_response.status_code,
            detail=_detalle(saga_response, 'No se pudo consultar el Saga Log'),
        )

    steps = saga_response.json().get('steps', [])
    saga_status = derive_status(steps)

    return PartnerRequestStatus(
        external_reference=external_reference,
        status=saga_status,
        work=await _obtener_work(external_reference),
        steps=[
            SagaStep(
                step=step.get('step', ''),
                status=step.get('status', ''),
                detail=step.get('detail', ''),
                created_at=step.get('created_at'),
            )
            for step in steps
        ],
    )


@router.get(
    '/works/{work_id}',
    response_model=WorkView,
    summary='Consulta un Work por id',
)
async def get_work(work_id: str) -> WorkView:
    response = await request_upstream(
        'GET',
        f'{settings.WORK_ORCHESTRATION_URL}/works/{work_id}',
        upstream='work-orchestration',
    )

    if response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Work {work_id} no encontrado',
        )
    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=_detalle(response, 'No se pudo consultar el Work'),
        )

    return _to_work_view(response.json())


async def _obtener_work(external_reference: str) -> WorkView | None:
    """El Work solo existe si las reglas aprobaron: su ausencia no es un error."""
    response = await request_upstream(
        'GET',
        f'{settings.WORK_ORCHESTRATION_URL}/works',
        upstream='work-orchestration',
        params={'external_reference': external_reference},
    )
    if response.status_code != status.HTTP_200_OK:
        return None
    return _to_work_view(response.json())


def _to_work_view(body: dict) -> WorkView:
    location = body.get('location') or {}
    return WorkView(
        id=str(body.get('id', '')),
        status=body.get('status', ''),
        partner_id=body.get('partner_id', ''),
        city=location.get('city', ''),
        country=location.get('country', ''),
        created_at=body.get('created_at', ''),
    )


def _detalle(response: Response, por_defecto: str) -> str:
    try:
        return response.json().get('detail', por_defecto)
    except ValueError:
        return por_defecto
