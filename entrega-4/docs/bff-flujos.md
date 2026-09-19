# BFF — Flujos de demostración

Guía de prueba manual de la POC a través del BFF. Cada flujo es copiar-pegar y
muestra la salida real esperada.

- Contrato completo de la API: [`bff-api.md`](bff-api.md)
- Arquitectura de la POC: [`architecture.md`](architecture.md)

---

## Cómo funciona el BFF

El **Backend For Frontend** es la única puerta de entrada pública del sistema.
No tiene dominio ni base de datos propia: recibe la solicitud del exterior, la
delega en los microservicios y agrega sus respuestas en un recurso único.

Sin él, demostrar una transacción exigía hablar con tres sitios distintos:
`POST` al puerto 8001, `GET /works` y `GET /sagas` al 8003, y leer
`docker logs` de Provider Matching.

```
                        Cliente (curl / Postman / tutor)
                                      |
                                      v
                        +---------------------------+
                        |        BFF  :8005         |   única puerta pública
                        |  no tiene dominio ni DB   |
                        +---------------------------+
                           |                     |
                 POST      |                     |  GET /sagas
            /partner-requests                    |  GET /works
                           v                     v
              +----------------------+   +----------------------+
              | Partner Integration  |   | Work Orchestration   |
              |    :8001  (ACL)      |   |   :8003  Saga Log    |
              +----------------------+   +----------------------+
                           |                     ^
        EvaluatePartnerRulesV1                   | PartnerRulesEvaluatedV1
                           v                     | MatchingCompletedV1
                    +--------------------------------+
                    |        Apache Pulsar           |
                    +--------------------------------+
                           |                     ^
                           v                     |
              +----------------------+   +----------------------+
              |   Partner Rules      |   |  Provider Matching   |
              |       :8002          |   |        :8004         |
              +----------------------+   +----------------------+
```

El BFF solo habla **HTTP** con dos servicios. Nunca publica en Pulsar ni toca
ninguna base de datos: eso preserva la autonomía de cada bounded context.

### La clave: `202` + recurso de estado

La SAGA es asíncrona y coreografiada. El `POST` **no** espera a que termine:
devuelve `202 Accepted` con el `external_reference`, la llave de correlación
que viaja en todos los eventos. Con ella se consulta el estado cuantas veces
haga falta.

| Estado | Significado |
|---|---|
| `PENDING` | Sin pasos registrados todavía |
| `IN_PROGRESS` | La SAGA avanza, sin resultado de matching |
| `COMPLETED` | Matching exitoso |
| `COMPENSATING` | Falló el matching, la compensación no ha terminado |
| `COMPENSATED` | El `Work` fue cancelado |
| `REJECTED` | Las reglas del partner rechazaron la solicitud |

Ningún servicio publica ese estado: en coreografía nadie es dueño del estado
global, así que **el BFF lo deriva** de los pasos del Saga Log.

---

## 0. Preparar

```bash
cd entrega-4
docker compose up -d
```


```bash
curl -s http://localhost:8005/api/v1/health | python3 -m json.tool
```


---

## Flujo 1 — Transacción exitosa

```bash
curl -X POST http://localhost:8005/api/v1/partner-requests \
  -H "Content-Type: application/json" \
  -d '{"partner_id":"partner-demo","payload":{"reference":"manual-ok-01","municipality":"Bogota","country_code":"CO","service_type":"HOME_REPAIR"}}'
```

→ `202` con `external_reference` y `status_url`.

```bash
curl -s http://localhost:8005/api/v1/partner-requests/manual-ok-01 | python3 -m json.tool
```

Si consultas de inmediato verás `IN_PROGRESS` con pasos parciales; a los ~5s:

```
status=COMPLETED   work=CREATED   [PARTNER_RULES_EVALUATED, WORK_CREATED, MATCHING_COMPLETED]
```



---

## Flujo 2 — Compensación

Igual, pero con `fail` en la referencia:

```bash
curl -X POST http://localhost:8005/api/v1/partner-requests \
  -H "Content-Type: application/json" \
  -d '{"partner_id":"partner-demo","payload":{"reference":"manual-fail-01","municipality":"Bogota","country_code":"CO","service_type":"HOME_REPAIR"}}'

sleep 6
curl -s http://localhost:8005/api/v1/partner-requests/manual-fail-01 | python3 -m json.tool
```

```
status=COMPENSATED   work=CANCELLED   [..., MATCHING_FAILED, WORK_CANCELLED]
```

El `Work` pasó a `CANCELLED`: la compensación revirtió el efecto, no solo
registró el fallo.

---

## Flujo 3 — Rechazo por reglas de negocio

`partner-demo` solo tiene regla para `HOME_REPAIR`. Manda otro `service_type`:

```bash
curl -X POST http://localhost:8005/api/v1/partner-requests \
  -H "Content-Type: application/json" \
  -d '{"partner_id":"partner-demo","payload":{"reference":"manual-rej-01","municipality":"Bogota","country_code":"CO","service_type":"PLUMBING"}}'

sleep 5
curl -s http://localhost:8005/api/v1/partner-requests/manual-rej-01 | python3 -m json.tool
```

```
status=REJECTED   work=null   [PARTNER_RULES_EVALUATED]
```

La saga se detuvo antes de crear el `Work`. Nada que compensar — es distinto
del flujo 2, y conviene decirlo explícitamente.

---

## Flujo 4 — Validación del ACL

```bash
curl -X POST http://localhost:8005/api/v1/partner-requests \
  -H "Content-Type: application/json" \
  -d '{"partner_id":"partner-demo","payload":{"municipality":"Bogota"}}'
```

→ `400 {"detail":"partner-demo requiere reference"}`

El BFF no valida nada: propaga el error del Anti-Corruption Layer. Demuestra
separación de responsabilidades.

---

## Flujo 5 — Tablero de monitoreo

```bash
curl -s "http://localhost:8005/api/v1/partner-requests?limit=10" | python3 -m json.tool
```

Los tres desenlaces en una sola llamada — `COMPLETED`, `COMPENSATED`,
`REJECTED`. Esto es lo que cubre *"monitorear el estado de las transacciones"*.

---

---

## — Swagger

<http://localhost:8005/docs> — las 6 rutas, con *Try it out* para ejecutar sin
terminal. Útil si no quieres mostrar curl en el video.

---
