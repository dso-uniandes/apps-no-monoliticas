#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXPERIMENT_DIR="${ROOT_DIR}/experiments/deployability"
MESSAGES="${1:-100}"

if ! [[ "${MESSAGES}" =~ ^[1-9][0-9]*$ ]]; then
  echo "Usage: $0 <positive-message-count-per-version>" >&2
  exit 2
fi

RUN_ID="$(date -u +%Y%m%d%H%M%S)"
export EXPERIMENT_TOPIC="persistent://public/default/hda-work-created-compat-${RUN_ID}"
export EXPERIMENT_SUBSCRIPTION="hda-provider-matching-v1-compat-${RUN_ID}"
COMPOSE=(docker compose -p hda-deployability -f "${ROOT_DIR}/docker-compose.yml" -f "${EXPERIMENT_DIR}/docker-compose.deployability.yml")
RESULTS_DIR="${EXPERIMENT_DIR}/results"
LOG_FILE="${RESULTS_DIR}/provider-matching.log"
RESULT_FILE="${RESULTS_DIR}/results.json"
CONSUMER_FILE="${ROOT_DIR}/src/provider_matching/infraestructura/mensajeria/work_created_consumer.py"

cleanup() {
  "${COMPOSE[@]}" down --volumes --remove-orphans >/dev/null 2>&1 || true
}

mkdir -p "${RESULTS_DIR}"
cleanup
trap cleanup EXIT

CONSUMER_CHECKSUM_BEFORE="$(shasum -a 256 "${CONSUMER_FILE}" | awk '{print $1}')"

"${COMPOSE[@]}" build provider-matching
"${COMPOSE[@]}" up -d --wait zookeeper bookie broker
"${COMPOSE[@]}" exec -T broker bin/pulsar-admin namespaces \
  set-schema-compatibility-strategy --compatibility FULL public/default
"${COMPOSE[@]}" up -d --no-deps provider-matching

# Wait until the real V1 consumer has created its durable subscription.
for _ in $(seq 1 60); do
  if curl -fsS "http://localhost:18080/admin/v2/persistent/public/default/${EXPERIMENT_TOPIC##*/}/stats" \
    | grep -q "${EXPERIMENT_SUBSCRIPTION}"; then
    break
  fi
  sleep 1
done

publish_version() {
  local version="$1"
  "${COMPOSE[@]}" run --rm --no-deps \
    -v "${ROOT_DIR}:/workspace:ro" \
    -e PYTHONPATH=/workspace/src:/app \
    provider-matching \
    python /workspace/experiments/deployability/publish_work_created.py \
    --topic "${EXPERIMENT_TOPIC}" \
    --version "${version}" \
    --messages "${MESSAGES}"
}

publish_version 1
publish_version 2

python3 "${EXPERIMENT_DIR}/wait_for_backlog.py" \
  --topic-name "${EXPERIMENT_TOPIC##*/}" \
  --subscription "${EXPERIMENT_SUBSCRIPTION}" \
  --timeout 60

# Capture the consumer output after both schema revisions have been handled.
"${COMPOSE[@]}" logs --no-color provider-matching > "${LOG_FILE}"
CONSUMER_CHECKSUM_AFTER="$(shasum -a 256 "${CONSUMER_FILE}" | awk '{print $1}')"

python3 "${EXPERIMENT_DIR}/collect_result.py" \
  --topic-name "${EXPERIMENT_TOPIC##*/}" \
  --subscription "${EXPERIMENT_SUBSCRIPTION}" \
  --messages-per-version "${MESSAGES}" \
  --consumer-log "${LOG_FILE}" \
  --consumer-checksum-before "${CONSUMER_CHECKSUM_BEFORE}" \
  --consumer-checksum-after "${CONSUMER_CHECKSUM_AFTER}" \
  --output "${RESULT_FILE}"

python3 "${EXPERIMENT_DIR}/write_summary.py" "${RESULT_FILE}" "${RESULTS_DIR}/summary.md"
