from fastapi import APIRouter

from provider_matching.config.settings import settings

router = APIRouter()


@router.get('/health')
async def health() -> dict[str, str]:
    return {
        'service': settings.SERVICE_NAME,
        'status': 'ok',
    }
