from fastapi import FastAPI
from cliente.config.api import app_configs

app = FastAPI(**app_configs)


@app.get("/health", include_in_schema=False)
async def health() -> dict[str, str]:
    return {"status": "ok"}
