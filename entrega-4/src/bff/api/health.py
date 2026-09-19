import asyncio

import httpx
from fastapi import APIRouter

from bff.config.settings import settings
from bff.infraestructura.http_clients import get_client

router = APIRouter()

_UPSTREAMS = {
    'partner-integration': settings.PARTNER_INTEGRATION_URL,
    'partner-rules': settings.PARTNER_RULES_URL,
    'work-orchestration': settings.WORK_ORCHESTRATION_URL,
    'provider-matching': settings.PROVIDER_MATCHING_URL,
}


@router.get('/health')
async def health() -> dict[str, str]:
    return {'service': settings.SERVICE_NAME, 'status': 'ok'}


@router.get('/api/v1/health', tags=['health'])
async def health_agregado() -> dict:
    """Estado consolidado de los cuatro microservicios de la POC."""
    nombres = list(_UPSTREAMS)
    resultados = await asyncio.gather(
        *(_check(_UPSTREAMS[nombre]) for nombre in nombres)
    )
    servicios = dict(zip(nombres, resultados))
    return {
        'service': settings.SERVICE_NAME,
        'status': 'ok' if all(v == 'ok' for v in servicios.values()) else 'degraded',
        'upstreams': servicios,
    }


async def _check(base_url: str) -> str:
    try:
        response = await get_client().get(f'{base_url}/health')
    except httpx.HTTPError:
        return 'unreachable'
    return 'ok' if response.status_code == 200 else f'error:{response.status_code}'
