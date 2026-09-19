from fastapi import APIRouter, Depends, Query

from work_orchestration.config.container import get_saga_log
from work_orchestration.infraestructura.saga_log import SagaLog

router = APIRouter()


@router.get('/sagas/{external_reference}')
def get_saga(
    external_reference: str,
    saga_log: SagaLog = Depends(get_saga_log),
) -> dict:
    return {
        'external_reference': external_reference,
        'steps': saga_log.get_steps(external_reference),
    }


@router.get('/sagas')
def list_sagas(
    limit: int = Query(default=50, ge=1, le=200),
    saga_log: SagaLog = Depends(get_saga_log),
) -> dict:
    sagas = saga_log.list_sagas(limit=limit)
    return {'total': len(sagas), 'sagas': sagas}
