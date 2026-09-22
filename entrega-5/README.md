# Entrega 5 - Prueba de concepto final | Hogar de los Alpes

Esta entrega contiene la POC final de Hogar de los Alpes. El sistema está separado en cuatro microservicios, usa Apache Pulsar para la comunicación asíncrona y expone el flujo al exterior únicamente por medio del BFF. También dejamos los experimentos finales de calidad, la SAGA con compensación y todo lo necesario para levantar y probar la solución.

## Arquitectura y estructura del proyecto

El flujo entra por el BFF. Partner Integration recibe y normaliza el request del partner. Partner Rules evalúa las reglas. Work Orchestration crea o cancela el `Work`. Provider Matching hace el matching. Entre ellos no hay HTTP: se hablan por contratos Avro sobre Pulsar.

| Componente | Responsabilidad |
|---|---|
| BFF | Única API pública: arranca el flujo y consolida el estado de la SAGA |
| Partner Integration | ACL B2B2C: normaliza el payload externo y publica `EvaluatePartnerRulesV1` |
| Partner Rules | Evalúa reglas/SLA del partner y publica `PartnerRulesEvaluatedV1` |
| Work Orchestration | Crea el `Work`, publica `WorkCreatedV1` y aplica compensación si el matching falla |
| Provider Matching | Consume `WorkCreatedV1` y publica `MatchingCompletedV1` o `MatchingFailedV1` |
| Apache Pulsar | Broker de commands/events |
| Persistencia | PI/PR/PM: SQLite; WO: PostgreSQL (+ Saga Log SQLite en la POC) |

Carpetas principales:

```text
src/                  Código de los microservicios y BFF
deploy/               Manifiestos de despliegue
infra/                Infraestructura (Terraform)
experiments/          Experimentos de calidad y resultados
docs/                 Documentación técnica
postman/              Collection y environment de Postman
scripts/              Automatización de build, deploy y verificación
tests/                Pruebas automatizadas
```

Detalle arquitectónico: [`docs/architecture.md`](docs/architecture.md).

## Sobre el flujo probado

A nivel de negocio, todo este flujo empieza cuando un partner necesita solicitar un trabajo para uno de sus clientes. Ese partner no tiene que conocer cómo funciona internamente Hogar de los Alpes ni cómo están divididos nuestros servicios: simplemente envía su solicitud por medio del BFF.

A partir de ahí, Partner Integration se encarga de traducir la solicitud del partner al formato que entiende nuestro sistema. Partner Rules aplica las condiciones y reglas particulares de ese partner y, si todo está correcto, Work Orchestration crea y administra el trabajo que debe atenderse.

Una vez existe el trabajo, el sistema publica el evento correspondiente para que Provider Matching pueda buscar qué proveedor podría atenderlo. Es decir, técnicamente vemos una cadena de llamadas, eventos y bounded contexts, pero a nivel de negocio lo que realmente estamos haciendo es recibir una solicitud externa, convertirla en un trabajo interno de Hogar de los Alpes y empezar el proceso para encontrar quién lo va a atender.

## Escenarios de calidad probados

| Escenario | Qué queríamos comprobar | Criterio principal | Resultado | Evidencia |
|---|---|---|---|---|
| Modificabilidad / configurabilidad | Agregar un partner nuevo tocando como máximo Partner Integration y Partner Rules, sin cambios en Work Orchestration | ≤ 2 BC modificados; 0 cambios en WO | PASS | [`experiments/modifiability/results/`](experiments/modifiability/results/) |
| Escalabilidad | Procesar al menos el 95 % de 10.000 trabajos acumulados en 60 s | ≥ 95 % en la ventana | PASS (1 consumidor) y PASS (4 consumidores) | [`experiments/scalability/results/`](experiments/scalability/results/) |
| Desplegabilidad / compatibilidad | Evolucionar `WorkCreated` a V2 y mantener operativo al consumidor V1 sin cambios | V1 y V2 procesados; backlog 0; 0 errores; 0 cambios al consumidor | PASS | [`experiments/deployability/results/`](experiments/deployability/results/) |

El análisis cualitativo completo de estos resultados está en [`docs/resultados-cualitativos.md`](docs/resultados-cualitativos.md).

## Cómo ejecutar localmente

Prerrequisitos: Docker y Docker Compose.

```bash
cd entrega-5
docker compose up --build -d
```

Para revisar que quedó arriba:

```bash
docker compose ps
curl http://localhost:8005/api/v1/health
```

- BFF local: <http://localhost:8005>
- Swagger local: <http://localhost:8005/docs>

Los flujos paso a paso con `curl` están en [`docs/bff-flujos.md`](docs/bff-flujos.md).

Apagar (conserva volúmenes):

```bash
docker compose down
```

## BFF — punto de entrada del sistema

**El BFF es la única API pública que debe utilizarse para interactuar con la POC.**

Los microservicios internos no se exponen para uso de cliente: en local quedan detrás de Compose y en GCP van como `ClusterIP`.

| Ambiente | Base URL | Swagger |
|---|---|---|
| Local | `http://localhost:8005` | `http://localhost:8005/docs` |
| GCP | `http://136.64.180.29` | `http://136.64.180.29/docs` |

Endpoints principales del BFF:

| Método | Ruta | Para qué |
|---|---|---|
| `GET` | `/health` | Health del BFF |
| `GET` | `/api/v1/health` | Health agregado (BFF + upstreams) |
| `POST` | `/api/v1/partner-requests` | Arranca el flujo (HTTP 202) |
| `GET` | `/api/v1/partner-requests/{external_reference}` | Estado consolidado de la SAGA |
| `GET` | `/api/v1/partner-requests?limit=20` | Listado reciente |
| `GET` | `/api/v1/works/{work_id}` | Consulta de un Work |

Contrato y payloads: [`docs/bff-api.md`](docs/bff-api.md).  
Demostración de flujos: [`docs/bff-flujos.md`](docs/bff-flujos.md).

## Postman

Los archivos están en el repo:

- Collection: [`postman/HDA-Entrega5-GCP.postman_collection.json`](postman/HDA-Entrega5-GCP.postman_collection.json)
- Environment: [`postman/HDA-Entrega5-GCP.postman_environment.json`](postman/HDA-Entrega5-GCP.postman_environment.json)

Cómo usarlos:

1. En Postman: **Import** → seleccionar la collection y el environment.
2. Activar el environment `HDA Entrega5 GCP`.
3. Revisar la variable `bff_url` (hoy apunta a `http://136.64.180.29`; en local se puede cambiar a `http://localhost:8005`).
4. Correr las carpetas en orden: Health → Saga exitosa → Compensación → Reglas rechazadas → Consultas.

Toda la collection habla únicamente con el BFF (`{{bff_url}}`). No hay requests directos a Partner Integration, Partner Rules, Work Orchestration ni Provider Matching.

## Despliegue

Proyecto GCP: `alpine-land-507822-t7`  
Cluster: `hda-poc` (`us-central1-a`)  
Artifact Registry: `us-central1-docker.pkg.dev/alpine-land-507822-t7/hda-poc`

Autenticación y proyecto:

```bash
cd entrega-5
gcloud auth login
gcloud auth application-default login
gcloud config set project alpine-land-507822-t7
export PROJECT_ID=alpine-land-507822-t7
export IMAGE_TAG=$(git rev-parse --short HEAD)-$(date +%Y%m%d%H%M)
```

Credenciales del cluster:

```bash
gcloud container clusters get-credentials hda-poc \
  --zone us-central1-a \
  --project alpine-land-507822-t7
```

Build, deploy y verificación (targets del `Makefile`):

```bash
make build    # scripts/build-and-push.sh
make deploy   # scripts/deploy-gcp.sh
make verify   # scripts/verify-gcp.sh
```

`make verify` toma la External IP del LoadBalancer del BFF, hace health, crea un partner request y espera a que el BFF reporte `COMPLETED`.

Estado actual desplegado (referencia):

| Campo | Valor |
|---|---|
| IMAGE_TAG | `e5-202609192043` |
| BFF público | `http://136.64.180.29` |
| Swagger | `http://136.64.180.29/docs` |

## Documentación

| Documento | Para qué sirve |
|---|---|
| [`docs/architecture.md`](docs/architecture.md) | Arquitectura de la POC |
| [`docs/bff-api.md`](docs/bff-api.md) | Contrato del BFF |
| [`docs/bff-flujos.md`](docs/bff-flujos.md) | Flujos de demostración paso a paso |
| [`docs/resultados-cualitativos.md`](docs/resultados-cualitativos.md) | Interpretación de los experimentos de calidad |
| [`experiments/modifiability/results/`](experiments/modifiability/results/) | Evidencia de modificabilidad |
| [`experiments/scalability/results/`](experiments/scalability/results/) | Evidencia de escalabilidad |
| [`experiments/deployability/results/`](experiments/deployability/results/) | Evidencia de desplegabilidad |


## Video 
https://drive.google.com/file/d/18DXhC8LRsz-fKT8ShC7upJgX27_o_BI2/view?usp=sharing 