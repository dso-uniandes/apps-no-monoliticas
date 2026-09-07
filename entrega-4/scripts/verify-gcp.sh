#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Pods / Services"
kubectl -n hda get pods,svc -o wide

EXTERNAL_IP=""
for _ in $(seq 1 30); do
  EXTERNAL_IP="$(kubectl -n hda get svc work-orchestration -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || true)"
  if [[ -n "${EXTERNAL_IP}" ]]; then
    break
  fi
  echo "Esperando External IP de work-orchestration..."
  sleep 10
done

if [[ -z "${EXTERNAL_IP}" ]]; then
  echo "ERROR: no se obtuvo External IP del LoadBalancer." >&2
  exit 1
fi

echo "==> External IP: ${EXTERNAL_IP}"
echo "==> Health WO"
curl -fsS "http://${EXTERNAL_IP}/health"
echo

PAYLOAD='{"partner_id":"partner-1","external_reference":"ext-gcp-1","location":{"city":"Bogota","country":"CO"}}'
echo "==> POST /works"
RESP="$(curl -fsS -X POST "http://${EXTERNAL_IP}/works" \
  -H "Content-Type: application/json" \
  -d "${PAYLOAD}")"
echo "${RESP}"
WORK_ID="$(python -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<<"${RESP}" 2>/dev/null \
  || python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<<"${RESP}")"

sleep 5
echo "==> Logs Work Orchestration (últimas líneas)"
kubectl -n hda logs deploy/work-orchestration -c work-orchestration --tail=50 | grep -E 'Work persisted|WorkCreatedV1 published' || true

echo "==> Logs Provider Matching (últimas líneas)"
kubectl -n hda logs deploy/provider-matching --tail=50 | grep -E 'WorkCreatedV1 received|Matching processed' || true

echo "==> Reinicio WO para probar persistencia Cloud SQL"
kubectl -n hda rollout restart deployment/work-orchestration
kubectl -n hda rollout status deployment/work-orchestration --timeout=300s

echo "==> GET /works/${WORK_ID}"
curl -fsS "http://${EXTERNAL_IP}/works/${WORK_ID}"
echo
echo "==> Verify OK"
