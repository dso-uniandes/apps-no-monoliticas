from fastapi import APIRouter

from partner_rules.config.settings import settings

router = APIRouter()


@router.get('/health')
async def health() -> dict[str, str]:
    return {
        'service': settings.SERVICE_NAME,
        'status': 'ok',
    }
