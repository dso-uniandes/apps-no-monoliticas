from fastapi import APIRouter

from partner_integration.config.settings import settings

router = APIRouter()


@router.get('/health')
async def health() -> dict[str, str]:
    return {
        'service': settings.SERVICE_NAME,
        'status': 'ok',
    }
