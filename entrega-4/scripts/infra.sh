#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TF_DIR="${ROOT_DIR}/infra/terraform"

PROJECT_ID="${PROJECT_ID:-$(gcloud config get-value project 2>/dev/null || true)}"
REGION="${REGION:-us-central1}"
ZONE="${ZONE:-us-central1-a}"
ENVIRONMENT="${ENVIRONMENT:-dev}"

if [[ -z "${PROJECT_ID}" || "${PROJECT_ID}" == "(unset)" ]]; then
  echo "ERROR: define PROJECT_ID o configura un proyecto activo en gcloud." >&2
  exit 1
fi

if [[ ! -f "${TF_DIR}/backend.hcl" ]]; then
  echo "ERROR: falta ${TF_DIR}/backend.hcl. Ejecuta primero: make bootstrap" >&2
  exit 1
fi

if [[ ! -f "${TF_DIR}/terraform.tfvars" ]]; then
  cat > "${TF_DIR}/terraform.tfvars" <<EOF
project_id  = "${PROJECT_ID}"
region      = "${REGION}"
zone        = "${ZONE}"
environment = "${ENVIRONMENT}"
EOF
  echo "Generado terraform.tfvars (no se versiona)."
fi

cd "${TF_DIR}"
terraform init -input=false -backend-config=backend.hcl
terraform fmt -recursive
terraform validate
terraform plan -out=tfplan
terraform apply -auto-approve tfplan
rm -f tfplan

echo "==> Infra lista."
terraform output
