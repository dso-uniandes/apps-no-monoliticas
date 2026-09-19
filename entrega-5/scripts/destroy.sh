#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TF_DIR="${ROOT_DIR}/infra/terraform"

echo "ADVERTENCIA: esto destruye la infraestructura GCP de la POC."
echo "No se ejecuta automáticamente. Confirma con: CONFIRM_DESTROY=yes make destroy"
if [[ "${CONFIRM_DESTROY:-}" != "yes" ]]; then
  exit 1
fi

cd "${TF_DIR}"
terraform destroy -auto-approve
