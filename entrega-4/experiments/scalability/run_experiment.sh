#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXPERIMENT_DIR="${ROOT_DIR}/experiments/scalability"
CONSUMERS="${1:-1}"
MESSAGES=10000
DURATION=60

if ! [[ "${CONSUMERS}" =~ ^[1-9][0-9]*$ ]]; then
  echo "Usage: $0 <positive-consumer-count>" >&2
  exit 2
fi

RUN_ID="$(date -u +%Y%m%d%H%M%S)-${CONSUMERS}"
export EXPERIMENT_TOPIC="persistent://public/default/hda-work-created-scale-${RUN_ID}"
export EXPERIMENT_SUBSCRIPTION="hda-provider-matching-scale-${RUN_ID}"
COMPOSE=(docker compose -p hda-scale -f "${ROOT_DIR}/docker-compose.yml" -f "${EXPERIMENT_DIR}/docker-compose.scalability.yml")

cleanup() {
  "${COMPOSE[@]}" down --volumes --remove-orphans >/dev/null 2>&1 || true
}

# BookKeeper stores its advertised address in its data volume. Every run uses a
# clean, isolated hda-scale cluster so a changed Docker IP cannot invalidate it.
cleanup
trap cleanup EXIT

"${COMPOSE[@]}" up -d zookeeper bookie broker
"${COMPOSE[@]}" up -d --scale provider-matching=0 provider-matching

"${COMPOSE[@]}" run --rm --no-deps \
  -v "${ROOT_DIR}:/workspace:ro" \
  provider-matching \
  python /workspace/experiments/scalability/publish_work_created.py \
  --pulsar-url pulsar://broker:6650 \
  --listener-name internal \
  --topic "${EXPERIMENT_TOPIC}" \
  --subscription "${EXPERIMENT_SUBSCRIPTION}" \
  --messages "${MESSAGES}"

STARTED_AT="$(python3 -c 'import time; print(time.time())')"
"${COMPOSE[@]}" up -d --scale provider-matching="${CONSUMERS}" provider-matching

python3 "${EXPERIMENT_DIR}/collect_result.py" \
  --topic-name "${EXPERIMENT_TOPIC##*/}" \
  --subscription "${EXPERIMENT_SUBSCRIPTION}" \
  --messages "${MESSAGES}" \
  --consumers "${CONSUMERS}" \
  --duration "${DURATION}" \
  --started-at "${STARTED_AT}" \
  --output "${EXPERIMENT_DIR}/results/consumers-${CONSUMERS}.json"
