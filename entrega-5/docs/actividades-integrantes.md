# Actividades por integrante

Este documento resume las principales actividades realizadas por cada integrante
durante la Entrega 5 de la POC de Hogar de los Alpes.

| Integrante | Actividades realizadas | Evidencia |
|---|---|---|
| Jose Fonseca | Implementacion de la SAGA coreografiada con eventos. Definicion de eventos `MatchingCompletedV1`, `MatchingFailedV1` y `WorkCancelledV1`. Implementacion de la compensacion cuando Provider Matching falla. Ajustes en Work Orchestration para cancelar el `Work` y registrar pasos en el Saga Log. Pruebas locales del flujo exitoso y compensado. | Commits relacionados con SAGA, `scripts/demo-saga-local.sh`, cambios en `src/work_orchestration`, `src/provider_matching` y `src/published_language`. |
| Juan Jose Ortiz | Implementacion del BFF como unica API publica. Creacion de endpoints para iniciar solicitudes, consultar estado consolidado de la SAGA, listar solicitudes recientes y consultar health agregado. Documentacion de uso del BFF. | `src/bff`, `bff.Dockerfile`, `deploy/k8s/bff.yaml`, `docs/bff-api.md`, `docs/bff-flujos.md`. |
| Daniel Serna | Preparacion del despliegue en GCP, manifiestos Kubernetes, scripts de build/deploy/verify y configuracion de la IP publica del BFF. Validacion del flujo desplegado. | `deploy/k8s`, `infra/terraform`, `scripts/build-and-push.sh`, `scripts/deploy-gcp.sh`, `scripts/verify-gcp.sh`, README seccion despliegue. |
| Eduardo Castro | Elaboracion de la coleccion de Postman, actualizacion del mapa de contexto, documentacion de resultados cualitativos y consolidacion de evidencias de experimentos de calidad. | `postman/`, `docs/context-map/`, `docs/resultados-cualitativos.md`, `experiments/*/results/`. |

## Resumen general

Durante la Entrega 5 se consolido la POC final con microservicios orientados a
eventos usando Apache Pulsar. Se agrego una SAGA coreografiada con compensacion,
se incorporo un BFF como unica entrada publica, se preparo el despliegue en GCP
y se documentaron los resultados de los escenarios de calidad definidos
previamente.

La solucion permite demostrar un flujo exitoso y un flujo con compensacion,
ambos consultables desde el BFF y probables mediante Postman o scripts locales.
