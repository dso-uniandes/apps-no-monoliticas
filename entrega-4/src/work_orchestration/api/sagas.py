from fastapi import APIRouter, Depends

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
