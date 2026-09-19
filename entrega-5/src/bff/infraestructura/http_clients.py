import logging

import httpx
from fastapi import HTTPException, status

from bff.config.settings import settings

logger = logging.getLogger(__name__)

_client: httpx.AsyncClient | None = None


def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT_SECONDS)
    return _client


async def close_client() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


async def request_upstream(
    method: str,
    url: str,
    upstream: str,
    **kwargs,
) -> httpx.Response:
    """Llama a un microservicio y traduce sus fallos a errores del BFF.

    El BFF no tiene dominio propio: si el upstream responde un error de negocio
    (4xx) se propaga tal cual; si no responde, se reporta como 502/504.
    """
    try:
        response = await get_client().request(method, url, **kwargs)
    except httpx.TimeoutException as exc:
        logger.warning('Timeout llamando a %s (%s)', upstream, url)
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f'{upstream} no respondio a tiempo',
        ) from exc
    except httpx.HTTPError as exc:
        logger.warning('Error de red llamando a %s (%s): %s', upstream, url, exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f'{upstream} no esta disponible',
        ) from exc

    if response.status_code >= 500:
        logger.warning('%s respondio %s', upstream, response.status_code)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f'{upstream} respondio {response.status_code}',
        )

    return response
