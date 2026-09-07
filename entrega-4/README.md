## Qué hay
- Local: Docker Compose | GCP: Terraform + K8s (sin Helm)

## Local
```bash
docker compose up --build
```

| Puerto | Servicio |
|---|---|
| 8001 | Partner Integration |
| 8002 | Partner Rules |
| 8003 | Work Orchestration |
| 8004 | Provider Matching |

```bash
curl -X POST http://localhost:8003/works \
  -H "Content-Type: application/json" \
  -d "{\"partner_id\":\"partner-1\",\"external_reference\":\"ext-100\",\"location\":{\"city\":\"Bogota\",\"country\":\"CO\"}}"
```

Flujo: Work Orchestrator MVP → PostgreSQL → Pulsar → Provider Matching

Apagar: `docker compose down` (sin `-v`)

## GCP
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

Pulsar en GKE es standalone + emptyDir (simplificación de la POC).  

Destruir (manual): `CONFIRM_DESTROY=yes make destroy`
