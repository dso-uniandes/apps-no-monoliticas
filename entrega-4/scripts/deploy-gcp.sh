#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TF_DIR="${ROOT_DIR}/infra/terraform"
K8S_DIR="${ROOT_DIR}/deploy/k8s"
RENDER_DIR="${ROOT_DIR}/.deploy-render"

PROJECT_ID="${PROJECT_ID:-$(gcloud config get-value project 2>/dev/null || true)}"
IMAGE_TAG="${IMAGE_TAG:-}"

if [[ -z "${PROJECT_ID}" || "${PROJECT_ID}" == "(unset)" ]]; then
  echo "ERROR: define PROJECT_ID o configura un proyecto activo en gcloud." >&2
  exit 1
fi

if [[ -z "${IMAGE_TAG}" && -f "${ROOT_DIR}/.image-tag" ]]; then
  IMAGE_TAG="$(cat "${ROOT_DIR}/.image-tag")"
fi
if [[ -z "${IMAGE_TAG}" ]]; then
  IMAGE_TAG="$(git -C "${ROOT_DIR}" rev-parse --short HEAD)"
fi

cd "${TF_DIR}"
CLUSTER_NAME="$(terraform output -raw gke_cluster_name)"
CLUSTER_LOCATION="$(terraform output -raw gke_cluster_location)"
ARTIFACT_REGISTRY="$(terraform output -raw artifact_registry_url)"
CLOUDSQL_CONNECTION_NAME="$(terraform output -raw cloud_sql_connection_name)"
WORK_ORCHESTRATION_GSA="$(terraform output -raw work_orchestration_gsa_email)"
DB_PASSWORD="$(terraform output -raw db_password)"
DB_USER="$(terraform output -raw db_user)"
DB_NAME="$(terraform output -raw db_name)"

echo "==> get-credentials cluster=${CLUSTER_NAME} location=${CLUSTER_LOCATION}"
gcloud container clusters get-credentials "${CLUSTER_NAME}" \
  --zone "${CLUSTER_LOCATION}" \
  --project "${PROJECT_ID}"

echo "==> upsert secret hda-db (password no se imprime)"
DATABASE_URL="postgresql+psycopg://${DB_USER}:${DB_PASSWORD}@127.0.0.1:5432/${DB_NAME}"
kubectl create namespace hda --dry-run=client -o yaml | kubectl apply -f -
kubectl -n hda create secret generic hda-db \
  --from-literal=password="${DB_PASSWORD}" \
  --from-literal=database_url="${DATABASE_URL}" \
  --dry-run=client -o yaml | kubectl apply -f -

rm -rf "${RENDER_DIR}"
mkdir -p "${RENDER_DIR}"

render() {
  local src="$1"
  local dst="${RENDER_DIR}/$(basename "${src}")"
  sed \
    -e "s|__ARTIFACT_REGISTRY__|${ARTIFACT_REGISTRY}|g" \
    -e "s|__IMAGE_TAG__|${IMAGE_TAG}|g" \
    -e "s|__CLOUDSQL_CONNECTION_NAME__|${CLOUDSQL_CONNECTION_NAME}|g" \
    -e "s|__WORK_ORCHESTRATION_GSA__|${WORK_ORCHESTRATION_GSA}|g" \
    "${src}" > "${dst}"
  echo "${dst}"
}

kubectl apply -f "$(render "${K8S_DIR}/namespace.yaml")"
kubectl apply -f "$(render "${K8S_DIR}/pulsar.yaml")"
kubectl apply -f "$(render "${K8S_DIR}/partner-integration.yaml")"
kubectl apply -f "$(render "${K8S_DIR}/partner-rules.yaml")"
kubectl apply -f "$(render "${K8S_DIR}/work-orchestration.yaml")"
kubectl apply -f "$(render "${K8S_DIR}/provider-matching.yaml")"

echo "==> waiting rollouts (tag=${IMAGE_TAG})"
kubectl -n hda rollout status deployment/pulsar --timeout=300s
kubectl -n hda rollout status deployment/partner-integration --timeout=180s
kubectl -n hda rollout status deployment/partner-rules --timeout=180s
kubectl -n hda rollout status deployment/work-orchestration --timeout=300s
kubectl -n hda rollout status deployment/provider-matching --timeout=300s

echo "==> Deploy listo."
kubectl -n hda get pods,svc
