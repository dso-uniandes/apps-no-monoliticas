# Entrega 4 - POC de arquitectura Hogar de los Alpes

POC de microservicios orientados a eventos en Python. Local con Docker Compose;
GCP con Terraform + GKE + Cloud SQL + Artifact Registry. Broker: Apache Pulsar.

## Alcance

| Requisito | Evidencia |
|---|---|
| 4 microservicios | `partner-integration`, `partner-rules`, `work-orchestration`, `provider-matching` |
| Commands + Events | Comandos locales + contratos Avro en Pulsar |
| Apache Pulsar | Compose + `deploy/k8s/pulsar.yaml` |
| Published Language | `EvaluatePartnerRulesV1`, `PartnerRulesEvaluatedV1`, `WorkCreatedV1/V2` |
| CRUD descentralizado | PI/PR/PM: SQLite; WO: PostgreSQL |
| Despliegue | Docker Compose y Terraform/GKE |

## Flujo asíncrono

```
Partner externo
      |
      | POST /partner-requests
      v
Partner Integration (ACL)
      |
      | EvaluatePartnerRulesV1 [COMMAND]
      v
Apache Pulsar
      |
      v
Partner Rules
      |
      | PartnerRulesEvaluatedV1 [INTEGRATION EVENT]
      v
Apache Pulsar
      |
      v
Work Orchestration
      |
      | WorkCreatedV1 [INTEGRATION EVENT]
      v
Apache Pulsar
      |
      v
Provider Matching
```

No hay HTTP entre microservicios. Solo se comparte Published Language.

Diagrama: `docs/architecture.puml`.

## SAGA Entrega 5

La SAGA se implementa por coreografia con eventos y abarca los 4 servicios:

1. `partner-integration` recibe `POST /partner-requests`, normaliza el payload y publica `EvaluatePartnerRulesV1`.
2. `partner-rules` consume el command, evalua reglas y publica `PartnerRulesEvaluatedV1`.
3. `work-orchestration` consume el resultado, crea el `Work`, publica `WorkCreatedV1` y escribe en el Saga Log.
4. `provider-matching` consume `WorkCreatedV1` y publica `MatchingCompletedV1` o `MatchingFailedV1`.

La compensacion ocurre en `work-orchestration`: cuando recibe `MatchingFailedV1`, cancela el `Work`, publica `WorkCancelledV1` y registra el paso en el Saga Log.

Para demostrar fallo se usa una referencia externa que contenga `fail`, por ejemplo `saga-fail-001`.

Consultar Saga Log:

```bash
curl http://localhost:8003/sagas/<external_reference>
```

Demo local de transaccion exitosa y compensada:

```bash
cd entrega-4
bash scripts/demo-saga-local.sh
```

## Experimentos de calidad

| Experimento | Estado |
|---|---|
| Modificabilidad / Configurabilidad | COMPLETO — PASS |
| Escalabilidad | COMPLETO — PASS |
| Desplegabilidad / Autonomía | COMPLETO — PASS |

Evidencia:

- `experiments/modifiability/results/`
- `experiments/scalability/results/`
- `experiments/deployability/results/`

### Desplegabilidad

Productor V1 y productor V2 publican al mismo topic `hda-work-created-v1`.
El consumidor V1 de Provider Matching procesa ambos sin cambios de código.
V2 agrega `region` y `priority` con defaults Avro; el broker usa estrategia
`FULL` (compatible hacia adelante y hacia atrás).

Criterios: 100 V1 + 100 V2 procesados, backlog 0, 0 errores de deserialización,
checksum del consumidor sin cambios.

```bash
cd entrega-4
bash experiments/deployability/run_experiment.sh
```

## Microservicios

| Servicio | Rol | Puerto |
|---|---|---|
| Partner Integration | ACL B2B2C: normaliza payload externo y publica el command | 8001 |
| Partner Rules | Evalúa reglas del partner y publica el resultado | 8002 |
| Work Orchestration | Crea Work si `allowed`, publica `WorkCreatedV1` | 8003 |
| Provider Matching | Consume `WorkCreatedV1` y ejecuta matching | 8004 |

Para Entrega 5, `partner-integration` funciona como BFF/API de entrada de la
POC y, al mismo tiempo, como Anti-Corruption Layer para payloads B2B2C.

## Published Language

| Contrato | Tipo | Uso |
|---|---|---|
| `EvaluatePartnerRulesV1` | COMMAND | PI → PR |
| `PartnerRulesEvaluatedV1` | INTEGRATION EVENT | PR → WO |
| `WorkCreatedV1` / `WorkCreatedV2` | INTEGRATION EVENT | WO → PM (evolución compatible) |
| `MatchingCompletedV1` | INTEGRATION EVENT | PM → monitoreo de SAGA |
| `MatchingFailedV1` | INTEGRATION EVENT | PM → WO para compensacion |
| `WorkCancelledV1` | INTEGRATION EVENT | WO publica la compensacion |

Los contratos están versionados, no exponen el modelo interno de cada BC y desacoplan productores/consumidores.

## Persistencia (CRUD)

Topología **descentralizada**: cada MS es dueño de sus datos. Ninguno lee tablas de otro.

| MS | Motor | Operaciones en repository |
|---|---|---|
| Partner Integration | SQLite | agregar, obtener_por_id, actualizar, eliminar |
| Partner Rules | SQLite | agregar, obtener_por_id, actualizar, eliminar, obtener_por_partner |
| Work Orchestration | PostgreSQL | agregar, obtener_por_id, actualizar, eliminar |
| Provider Matching | SQLite | agregar, obtener_por_id, actualizar, eliminar |

SQLite aquí es decisión de POC, no de producción.

## Ejecutar localmente

```bash
cd entrega-4
docker compose up --build -d
```

Entrada del flujo completo:

```bash
curl -X POST http://localhost:8001/partner-requests \
  -H "Content-Type: application/json" \
  -d '{"partner_id":"partner-demo","payload":{"reference":"EXT-LOCAL-001","municipality":"Bogota","country_code":"CO","service_type":"HOME_REPAIR"}}'
```

Health:

```bash
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
```

Logs esperados:

```bash
docker logs partner-integration | grep 'EvaluatePartnerRulesV1 published'
docker logs partner-rules | grep 'EvaluatePartnerRulesV1 received'
docker logs partner-rules | grep 'PartnerRulesEvaluatedV1 published'
docker logs work-orchestration | grep 'PartnerRulesEvaluatedV1 received'
docker logs work-orchestration | grep 'WorkCreatedV1 published'
docker logs provider-matching | grep 'Matching processed'
```

Probar compensacion de la SAGA:

```bash
FAIL_REF="saga-fail-$(date +%s)"
curl -X POST http://localhost:8001/partner-requests \
  -H "Content-Type: application/json" \
  -d "{\"partner_id\":\"partner-demo\",\"payload\":{\"reference\":\"${FAIL_REF}\",\"municipality\":\"Bogota\",\"country_code\":\"CO\",\"service_type\":\"HOME_REPAIR\"}}"

sleep 12
curl "http://localhost:8003/sagas/${FAIL_REF}"
docker logs provider-matching | grep 'MatchingFailedV1 published'
docker logs work-orchestration | grep 'WorkCancelledV1 published'
```

Apagar (conserva volúmenes):

```bash
docker compose down
```

## Despliegue en GCP

Proyecto: `alpine-land-507822-t7`.

**Estado: PASS** — E2E en GKE (`ext-gcp-1789426682`): PI → PR → WO → PM
(`EvaluatePartnerRulesV1` → `PartnerRulesEvaluatedV1` → `WorkCreatedV1` → Matching).

### Desplegar (si aún no está en el cluster)

```bash
cd entrega-4
gcloud auth login
gcloud auth application-default login
gcloud config set project alpine-land-507822-t7
export PROJECT_ID=alpine-land-507822-t7
export IMAGE_TAG=$(git rev-parse --short HEAD)-$(date +%Y%m%d%H%M)

make build
make deploy
```

### Prueba E2E en GCP (replicar)

Con el cluster ya desplegado, validar el flujo asíncrono completo:

```bash
cd entrega-4
gcloud container clusters get-credentials hda-poc \
  --zone us-central1-a \
  --project alpine-land-507822-t7

# Opción recomendada (script automatizado):
make verify
# equivale a: bash scripts/verify-gcp.sh
```

Qué hace `make verify` / `scripts/verify-gcp.sh`:

1. Obtiene la External IP del LoadBalancer de `partner-integration`.
2. `GET /health` → debe responder `{"service":"partner-integration","status":"ok"}`.
3. `POST /partner-requests` con un `reference` único (`ext-gcp-<timestamp>`).
4. Espera el flujo async y comprueba en logs:

| Paso | Servicio | Log esperado |
|---|---|---|
| 1 | Partner Integration | `EvaluatePartnerRulesV1 published: <REF>` |
| 2 | Partner Rules | `EvaluatePartnerRulesV1 received: <REF>` |
| 3 | Partner Rules | `PartnerRulesEvaluatedV1 published: <REF>` |
| 4 | Work Orchestration | `PartnerRulesEvaluatedV1 received: <REF>` |
| 5 | Work Orchestration | `Work persisted` + `WorkCreatedV1 published` |
| 6 | Provider Matching | `WorkCreatedV1 received` + `Matching processed` |

### Prueba E2E manual (sin script)

```bash
# External IP de Partner Integration
EXTERNAL_IP=$(kubectl -n hda get svc partner-integration \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

curl -fsS "http://${EXTERNAL_IP}/health"

REF="ext-gcp-$(date +%s)"
curl -fsS -X POST "http://${EXTERNAL_IP}/partner-requests" \
  -H "Content-Type: application/json" \
  -d "{\"partner_id\":\"partner-demo\",\"payload\":{\"reference\":\"${REF}\",\"municipality\":\"Bogota\",\"country_code\":\"CO\",\"service_type\":\"HOME_REPAIR\"}}"

# Esperar ~12s y revisar logs del flujo PI → PR → WO → PM
sleep 12
kubectl -n hda logs deploy/partner-integration --tail=80 | grep "EvaluatePartnerRulesV1 published"
kubectl -n hda logs deploy/partner-rules --tail=80 | grep -E "EvaluatePartnerRulesV1 received|PartnerRulesEvaluatedV1 published"
kubectl -n hda logs deploy/work-orchestration -c work-orchestration --tail=80 | grep -E "PartnerRulesEvaluatedV1 received|Work persisted|WorkCreatedV1 published"
kubectl -n hda logs deploy/provider-matching --tail=80 | grep -E "WorkCreatedV1 received|Matching processed"
```

Evidencia de la corrida del equipo: referencia `ext-gcp-1789426682`, HTTP `202 accepted`, flujo PI → PR → WO → PM completo en logs.
