# Entrega 3 — Diseño de Experimentación — Hogar de los Alpes

## Alcance
POC de **Work Orchestration** para sustentar decisiones de arquitectura de la Entrega 2. No pretende implementar todo HDA: implementa el corte mínimo necesario para experimentar atributos no funcionales.

## Principios demostrados
- DDD: Aggregate Root `Work`, Value Object `Location`, evento de dominio `WorkCreated`, repositorio como puerto.
- Arquitectura hexagonal: dominio y aplicación no dependen de FastAPI, PostgreSQL ni RabbitMQ.
- CQS: `CreateWorkCommand` modifica estado; `GetWorkQuery` consulta estado.
- Eventos: el módulo `work` publica `WorkCreated`; el módulo `assignment` lo consume. No hay llamada directa entre ambos.
- Persistencia real: PostgreSQL.
- Event broker: RabbitMQ.

## Estructura
- `src/work_orchestration/domain`: modelo y puertos.
- `application/commands`: comandos CQS.
- `application/queries`: consultas CQS.
- `infrastructure`: adaptadores PostgreSQL/RabbitMQ.
- `modules/assignment`: segundo módulo y consumidor de evento.
- `experiments`: prueba de carga k6.

## Ejecución
1. `docker compose up --build`
2. API: `POST http://localhost:8000/works`
3. Consulta: `GET http://localhost:8000/works/{id}`
4. Para consumir eventos en otra terminal/contenedor:
   `PYTHONPATH=src python -m work_orchestration.modules.assignment.consumer`

Ejemplo POST:
```json
{"category":"plomeria","urgency":"alta","city":"Bogota","zone":"Norte"}
```

## Escenarios de calidad
La presentación `Entrega3-HDA.pptx` contiene los 9 escenarios: 3 de escalabilidad, 3 de modificabilidad/configurabilidad y 3 de desplegabilidad/autonomía. Las cifras de prueba son **objetivos de diseño de la POC**, no cifras provistas literalmente por el caso, salvo donde se indica la escala del enunciado (millones de requests diarios, miles de trabajos diarios, 30+ partners).

## Experimento base
`k6 run experiments/k6_create_work.js`

Objetivo inicial de diseño: 500 creaciones/s durante 5 min, p95 < 1 s y error < 1%. Debe ajustarse/validarse con tutor y stakeholders; se escogió como carga de estrés por encima del promedio implícito en “millones de requests diarios”.

## Repositorio público
Subir esta carpeta a GitHub/GitLab público y reemplazar aquí:
`REPO_PUBLICO_PENDIENTE`

## Video
No incluido por solicitud del equipo.
