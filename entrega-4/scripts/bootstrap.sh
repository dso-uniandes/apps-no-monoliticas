#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BOOTSTRAP_DIR="${ROOT_DIR}/infra/bootstrap"

PROJECT_ID="${PROJECT_ID:-$(gcloud config get-value project 2>/dev/null || true)}"
REGION="${REGION:-us-central1}"

if [[ -z "${PROJECT_ID}" || "${PROJECT_ID}" == "(unset)" ]]; then
  echo "ERROR: define PROJECT_ID o configura un proyecto activo en gcloud." >&2
  exit 1
fi

echo "==> Bootstrap remote state bucket for project=${PROJECT_ID} region=${REGION}"
cd "${BOOTSTRAP_DIR}"
terraform init -input=false
terraform apply -auto-approve \
  -var="project_id=${PROJECT_ID}" \
  -var="region=${REGION}"

"${ROOT_DIR}/scripts/generate-backend-hcl.sh"

echo "==> Bootstrap listo. Siguiente: make infra"
