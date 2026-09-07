#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TF_DIR="${ROOT_DIR}/infra/terraform"

PROJECT_ID="${PROJECT_ID:-$(gcloud config get-value project 2>/dev/null || true)}"
REGION="${REGION:-}"
IMAGE_TAG="${IMAGE_TAG:-$(git -C "${ROOT_DIR}" rev-parse --short HEAD)}"

if [[ -z "${PROJECT_ID}" || "${PROJECT_ID}" == "(unset)" ]]; then
  echo "ERROR: define PROJECT_ID o configura un proyecto activo en gcloud." >&2
  exit 1
fi

if [[ -z "${REGION}" ]]; then
  if [[ -d "${TF_DIR}/.terraform" ]]; then
    REGION="$(terraform -chdir="${TF_DIR}" output -raw region 2>/dev/null || true)"
  fi
  REGION="${REGION:-us-central1}"
fi

REGISTRY="${REGION}-docker.pkg.dev/${PROJECT_ID}/hda-poc"

echo "==> Build + push tag=${IMAGE_TAG} registry=${REGISTRY}"

gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet

SERVICES=(
  "partner-integration:partner-integration.Dockerfile"
  "partner-rules:partner-rules.Dockerfile"
  "work-orchestration:work-orchestration.Dockerfile"
  "provider-matching:provider-matching.Dockerfile"
)

for entry in "${SERVICES[@]}"; do
  name="${entry%%:*}"
  dockerfile="${entry##*:}"
  image="${REGISTRY}/${name}:${IMAGE_TAG}"
  echo "---- building ${image}"
  docker build -f "${ROOT_DIR}/${dockerfile}" -t "${image}" "${ROOT_DIR}"
  docker push "${image}"
done

echo "==> Imágenes publicadas con tag: ${IMAGE_TAG}"
echo "${IMAGE_TAG}" > "${ROOT_DIR}/.image-tag"
