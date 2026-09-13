# Entrega 4 - POC de arquitectura Hogar de los Alpes

Esta carpeta contiene la prueba de concepto parcial para una arquitectura de microservicios orientada a eventos, desarrollada en Python y desplegable localmente con Docker Compose o en GCP con Terraform + Kubernetes.

La implementacion continua la linea definida en Entrega 3: Work Orchestration como capacidad central, CQS para escritura/lectura, arquitectura hexagonal, PostgreSQL para persistencia operacional y Published Language para eventos de trabajo. La diferencia principal es tecnologica y de alcance: Entrega 3 proponia RabbitMQ para la POC inicial, mientras que Entrega 4 exige Apache Pulsar y al menos 4 microservicios.

## Alcance de la entrega parcial

La POC cubre los puntos esperados para Entrega 4:

| Requisito | Evidencia en el repo |
|---|---|
| 4 microservicios en Python | `partner-integration`, `partner-rules`, `work-orchestration`, `provider-matching` |
| Comunicacion por comandos y eventos | Comandos en `src/*/aplicacion/comandos`, handlers en `src/*/aplicacion/handlers`, eventos de dominio y evento de integracion `WorkCreatedV1` |
| Broker Apache Pulsar | `docker-compose.yml`, `deploy/k8s/pulsar.yaml`, publicador y consumidor Pulsar |
| Esquema de eventos y evolucion | Avro con `published_language/v1/work_created.py` y `published_language/v2/work_created.py`; topic `hda-work-created-v1` y version en `schema_version` |
| Almacenamiento CRUD descentralizado | PostgreSQL para `work-orchestration`, SQLite propia para `partner-integration` y `provider-matching`; queda pendiente completar BD propia de `partner-rules` |
| Despliegue | Docker Compose local y Terraform + GKE + Cloud SQL + Artifact Registry |
| Verificacion funcional | Docker Compose, health checks, POST `/works`, logs de publicacion/consumo y verificacion de persistencia |

## Escenarios de calidad validados

Estos escenarios vienen de Entrega 3 y corresponden a los tres elegidos por el equipo para la entrega parcial:

| Experimento | Estado |
|---|---|
| Modificabilidad / Configurabilidad | COMPLETO — PASS |
| Escalabilidad | Preparado — pendiente ejecucion/medicion |
| Desplegabilidad / Autonomia | Preparado — pendiente ejecucion de compatibilidad |

| Atributo | Escenario de Entrega 3 | Validacion en esta POC |
|---|---|---|
| Escalabilidad | Pico de Provider Matching: 10.000 trabajos en cola; 95% procesados en menos de 60 s | Base tecnica lista: `provider-matching` consume `WorkCreatedV1` desde Pulsar con suscripcion `Shared`. Pendiente ejecutar la prueba de carga, medir backlog y documentar resultados |
| Modificabilidad / Configurabilidad | Incorporar un nuevo partner B2B2C sin modificar el agregado `Work`; cambio localizado en ACL/reglas | Experimento ejecutado con `partner-demo`: cambios solo en Partner Integration y Partner Rules; Work Orchestration sin cambios. Resultado: PASS. Evidencia en `experiments/modifiability/results/` |
| Desplegabilidad / Autonomia | Compatibilidad de evento versionado: consumidores v1 siguen operando mientras entra `WorkCreatedV2`; 0 errores de deserializacion | Base preparada: `published_language/v2` agrega campos con defaults y conserva todos los campos de `WorkCreatedV1`. Pendiente ejecutar la prueba de compatibilidad |

### Modificabilidad / Configurabilidad

Objetivo:
Incorporar un nuevo partner B2B2C sin modificar Work Orchestration.

Resultado experimental:

- Bounded Contexts modificados: 2
- Cambios en Work Orchestration: 0
- partner-demo soportado: Si
- Normalizacion: exitosa
- Reglas: exitosas
- Resultado: PASS

Evidencia:

`experiments/modifiability/results/`

Ejecucion:

```bash
cd entrega-4
PYTHONPATH=src python experiments/modifiability/run_experiment.py
```

## Microservicios

| Servicio | Responsabilidad | Puerto local |
|---|---|---|
| Partner Integration | BFF / capa anticorrupcion para normalizar solicitudes externas | 8001 |
| Partner Rules | Evalua reglas de partners | 8002 |
| Work Orchestration | Recibe `CreateWork`, persiste el agregado y publica `WorkCreatedV1` | 8003 |
| Provider Matching | Consume `WorkCreatedV1` y procesa el matching de proveedor | 8004 |

## Evento publicado

Se usa un **evento de integracion con carga de estado** (`WorkCreatedV1`) porque el consumidor no debe depender del modelo interno del agregado `Work`. El evento incluye los datos minimos para que `provider-matching` procese el comando local `ProcessMatching`.

Tecnologia elegida: **Avro sobre Apache Pulsar**, por compatibilidad nativa con `pulsar-client[avro]`, validacion de schema y evolucion versionada. La convencion actual es:

- Clase de contrato v1: `src/published_language/v1/work_created.py`
- Clase de contrato v2 compatible: `src/published_language/v2/work_created.py`
- Topic: `persistent://public/default/hda-work-created-v1`
- Campo de version: `schema_version='1'`
- Estrategia de evolucion: cambios compatibles agregan campos con default en `v2`; cambios incompatibles deben publicarse en un topic nuevo como `hda-work-created-v2`.

## Almacenamiento

La topologia es **descentralizada** para la POC local:

- Cada microservicio conserva su repositorio y su modelo de dominio.
- `work-orchestration` usa CRUD con PostgreSQL local o Cloud SQL en GCP.
- `partner-integration` y `provider-matching` usan SQLite propia con repositorios simples basados en `sqlite3` cuando corren en Docker Compose o Kubernetes.
- `partner-rules` conserva el esqueleto funcional con repositorio in-memory y queda como actividad separada para completar persistencia propia y evidencia de modificabilidad.
- Los repositorios in-memory siguen disponibles solo para pruebas unitarias y ejecuciones rapidas sin infraestructura.

No se implementa Event Sourcing en la entrega parcial porque el escenario validado requiere trazabilidad del evento de integracion y persistencia operacional basica, no reconstruccion completa por stream de eventos.

## Ejecutar localmente

```bash
cd entrega-4
docker compose up --build
```

Crear un work:

```bash
curl -X POST http://localhost:8003/works \
  -H "Content-Type: application/json" \
  -d '{"partner_id":"partner-1","external_reference":"ext-100","location":{"city":"Bogota","country":"CO"}}'
```

Verificar health checks:

```bash
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
```

Verificar flujo asincrono:

```bash
docker logs work-orchestration | grep 'WorkCreatedV1 published'
docker logs provider-matching | grep 'WorkCreatedV1 received'
docker logs provider-matching | grep 'Matching processed'
```

Verificar BD descentralizada local:

```bash
docker compose exec partner-integration ls -l /data
docker compose exec provider-matching ls -l /data
```

Apagar:

```bash
docker compose down
```

## Verificacion pendiente para el equipo

La POC se puede verificar manualmente con Docker Compose usando los comandos anteriores. Queda como actividad separada del equipo agregar pruebas automatizadas con `pytest` para handlers, contratos de eventos, repositorios y API.

El experimento de modificabilidad ya esta completo (PASS). Quedan pendientes de ejecucion:

- Escalabilidad de `provider-matching`: generar trabajos/eventos, observar backlog en Pulsar, escalar replicas/consumidores y reportar si se cumple el objetivo de procesar el 95% de 10.000 trabajos en menos de 60 s.
- Desplegabilidad / autonomia: ejecutar la prueba de compatibilidad entre consumidores v1 y `WorkCreatedV2`.

Base sugerida para quien tome esa actividad:

```bash
cd entrega-4
python3 -m venv .venv
. .venv/bin/activate
pip install -r hda-requirements.txt pytest httpx
pytest
```

## Despliegue en GCP

Requisitos: `gcloud`, `terraform`, `docker`, `kubectl`, `make`, bash.

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project <PROJECT_ID>
export PROJECT_ID=<PROJECT_ID>

make bootstrap
make infra
make build
make deploy
make verify
```

El despliegue crea Artifact Registry, red privada, GKE, Cloud SQL y manifiestos Kubernetes. Pulsar se despliega standalone en GKE con `emptyDir` como simplificacion de POC.

Destruir recursos:

```bash
CONFIRM_DESTROY=yes make destroy
```

## Actividades por miembro

Completar antes de entregar con nombres reales y evidencia de commits/PRs:

| Miembro | Actividades | Evidencia |
|---|---|---|
| Integrante 1 | Definicion de microservicios, comandos y dominio | Commits/PRs |
| Integrante 2 | Pulsar, published language y consumidores | Commits/PRs |
| Integrante 3 | Persistencia, Docker Compose y pruebas | Commits/PRs |
| Integrante 4 | Terraform, Kubernetes, documentacion y verificacion | Commits/PRs |

## Sustentacion rapida

- La arquitectura es event-driven: `CreateWork` persiste el agregado y publica `WorkCreatedV1`.
- Pulsar desacopla productor y consumidor; `provider-matching` puede escalar por suscripcion `Shared`.
- El contrato publicado esta versionado en `published_language/v1` y `published_language/v2`; no se expone el evento de dominio interno.
- La persistencia se mantiene por servicio en la base tecnica; `work-orchestration`, `partner-integration` y `provider-matching` ya tienen persistencia propia, y `partner-rules` queda pendiente para otro miembro.
- `make verify` prueba health, creacion de work, publicacion/consumo del evento y persistencia tras reiniciar el deployment.
