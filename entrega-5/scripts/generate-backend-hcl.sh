#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_FILE="${ROOT_DIR}/infra/terraform/backend.hcl"

PROJECT_ID="${PROJECT_ID:-$(gcloud config get-value project 2>/dev/null || true)}"
if [[ -z "${PROJECT_ID}" || "${PROJECT_ID}" == "(unset)" ]]; then
  echo "ERROR: define PROJECT_ID o configura un proyecto activo en gcloud." >&2
  exit 1
fi

cat > "${OUT_FILE}" <<EOF
bucket = "${PROJECT_ID}-hda-tfstate"
prefix = "hda-poc"
EOF

echo "Generado: ${OUT_FILE}"
echo "bucket = ${PROJECT_ID}-hda-tfstate"
