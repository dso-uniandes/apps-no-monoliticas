# BFF - Contrato de la API

El BFF (Backend For Frontend) es la **unica puerta de entrada publica** del
sistema. No tiene dominio ni base de datos propia: recibe la solicitud del
partner, la delega en los microservicios y agrega sus respuestas en un solo
recurso orientado al cliente.

```
Cliente (curl / Postman / partner)
        |
        v
      BFF  :8005  (unico LoadBalancer en GKE)
     /     \
    v       v
Partner    Work Orchestration
Integration  /sagas + /works
 (ACL)
```

Documentacion interactiva (OpenAPI): `http://localhost:8005/docs`.

Guia de prueba paso a paso: [`bff-flujos.md`](bff-flujos.md).

## Por que un 202 y no un 200 con el resultado

La SAGA es **coreografiada y asincrona**: Partner Integration publica un command
en Pulsar y devuelve el control de inmediato. Si el BFF esperara a que la SAGA
terminara, reintroduciria acoplamiento temporal entre los cuatro servicios,
que es justamente lo que el patron evita.

Por eso el BFF usa el patron estandar de operacion asincrona:
**`202 Accepted` + un recurso de estado consultable**. El POST devuelve el
`external_reference` (llave de correlacion de toda la SAGA) y el `status_url`
donde seguir el proceso.

## Endpoints

| Verbo | Ruta | Proposito |
|---|---|---|
| POST | `/api/v1/partner-requests` | Inicia la SAGA |
| GET | `/api/v1/partner-requests` | Tablero de monitoreo |
| GET | `/api/v1/partner-requests/{ref}` | Estado consolidado de una SAGA |
| GET | `/api/v1/works/{work_id}` | Consulta un Work por id |
| GET | `/api/v1/health` | Salud del BFF y los 4 microservicios |

### `POST /api/v1/partner-requests`

Inicia la SAGA. Delega en Partner Integration, que actua como Anti-Corruption
Layer del payload B2B2C.

```bash
curl -X POST http://localhost:8005/api/v1/partner-requests \
  -H "Content-Type: application/json" \
  -d '{"partner_id":"partner-demo","payload":{"reference":"saga-demo-001","municipality":"Bogota","country_code":"CO","service_type":"HOME_REPAIR"}}'
```

```json
{
  "status": "accepted",
  "partner_id": "partner-demo",
  "external_reference": "saga-demo-001",
  "partner_request_id": "0f6c...",
  "status_url": "/api/v1/partner-requests/saga-demo-001"
}
```

| Codigo | Significado |
|---|---|
| 202 | Solicitud aceptada, SAGA iniciada |
| 400 | Payload invalido (lo decide Partner Integration, el BFF lo propaga) |
| 502 / 504 | Partner Integration no disponible o sin respuesta a tiempo |

### `GET /api/v1/partner-requests/{external_reference}`

**Endpoint de agregacion.** Combina el Saga Log y el estado del `Work` de Work
Orchestration en una sola respuesta, y deriva un estado global de la SAGA.

```bash
curl http://localhost:8005/api/v1/partner-requests/saga-demo-001
```

```json
{
  "external_reference": "saga-demo-001",
  "status": "COMPLETED",
  "work": {
    "id": "8b1c...",
    "status": "CREATED",
    "partner_id": "partner-demo",
    "city": "Bogota",
    "country": "CO",
    "created_at": "2026-09-19T10:00:00"
  },
  "steps": [
    {"step": "PARTNER_RULES_EVALUATED", "status": "PASSED", "detail": "allowed=True"},
    {"step": "WORK_CREATED", "status": "DONE", "detail": "8b1c..."},
    {"step": "MATCHING_COMPLETED", "status": "DONE", "detail": "provider_id=prov-1"}
  ]
}
```

Estados derivados por el BFF a partir del Saga Log:

| `status` | Cuando |
|---|---|
| `PENDING` | Aun no hay pasos registrados |
| `IN_PROGRESS` | La SAGA avanza, sin resultado de matching |
| `COMPLETED` | Existe `MATCHING_COMPLETED` |
| `COMPENSATING` | Hubo `MATCHING_FAILED`, la compensacion no ha terminado |
| `COMPENSATED` | Existe `WORK_CANCELLED` (o la compensacion no hallo el Work) |
| `REJECTED` | Las reglas del partner rechazaron la solicitud |

`work` es `null` cuando las reglas rechazaron la solicitud o el `Work` aun no
se ha creado: no es un error.

La derivacion es **logica de presentacion**. En coreografia ningun servicio es
dueno del estado global, asi que el BFF lo infiere de la traza para responder
la unica pregunta que le importa al cliente: como va mi solicitud.

### `GET /api/v1/partner-requests`

**Tablero de monitoreo.** Lista las SAGAs mas recientes con su estado derivado,
sin necesidad de conocer sus referencias de antemano.

```bash
curl "http://localhost:8005/api/v1/partner-requests?limit=10"
```

```json
{
  "total": 3,
  "sagas": [
    {
      "external_reference": "saga-fail-1789851237",
      "status": "COMPENSATED",
      "last_step": "WORK_CANCELLED",
      "steps_count": 4,
      "updated_at": "2026-09-19 20:53:57",
      "status_url": "/api/v1/partner-requests/saga-fail-1789851237"
    }
  ]
}
```

`limit` acepta de 1 a 200 (50 por defecto). El `status` se deriva con la misma
funcion que la consulta individual, de modo que ambas vistas no pueden
contradecirse.

Se apoya en `GET /sagas?limit=N` de Work Orchestration.

### `GET /api/v1/works/{work_id}`

Consulta directa de un `Work` por id. Devuelve 404 si no existe.

### `GET /api/v1/health`

Estado consolidado del BFF y los cuatro microservicios.

```json
{
  "service": "bff",
  "status": "ok",
  "upstreams": {
    "partner-integration": "ok",
    "partner-rules": "ok",
    "work-orchestration": "ok",
    "provider-matching": "ok"
  }
}
```

`status` es `degraded` si algun upstream responde `unreachable` o con error.

## Demostrar la SAGA completa desde el BFF

```bash
cd entrega-4
docker compose up --build -d
bash scripts/demo-saga-local.sh
```
