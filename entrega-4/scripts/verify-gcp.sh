#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Pods / Services"
kubectl -n hda get pods,svc -o wide

EXTERNAL_IP=""
for _ in $(seq 1 30); do
  EXTERNAL_IP="$(kubectl -n hda get svc partner-integration -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || true)"
  if [[ -n "${EXTERNAL_IP}" ]]; then
    break
  fi
  echo "Esperando External IP de partner-integration..."
  sleep 10
done

if [[ -z "${EXTERNAL_IP}" ]]; then
  echo "ERROR: no se obtuvo External IP del LoadBalancer de partner-integration." >&2
  exit 1
fi

REF="ext-gcp-$(date +%s)"
echo "==> External IP PI: ${EXTERNAL_IP}"
echo "==> Health PI"
curl -fsS "http://${EXTERNAL_IP}/health"
echo

PAYLOAD="$(cat <<EOF
{"partner_id":"partner-demo","payload":{"reference":"${REF}","municipality":"Bogota","country_code":"CO","service_type":"HOME_REPAIR"}}
EOF
)"

echo "==> POST /partner-requests (${REF})"
RESP="$(curl -fsS -X POST "http://${EXTERNAL_IP}/partner-requests" \
  -H "Content-Type: application/json" \
  -d "${PAYLOAD}")"
echo "${RESP}"

echo "==> Esperando flujo asíncrono..."
sleep 12

echo "==> Logs Partner Integration"
kubectl -n hda logs deploy/partner-integration --tail=80 | grep -E "EvaluatePartnerRulesV1 published" || true

echo "==> Logs Partner Rules"
kubectl -n hda logs deploy/partner-rules --tail=80 | grep -E "EvaluatePartnerRulesV1 received|PartnerRulesEvaluatedV1 published" || true

echo "==> Logs Work Orchestration"
kubectl -n hda logs deploy/work-orchestration -c work-orchestration --tail=80 | grep -E "PartnerRulesEvaluatedV1 received|Work persisted|WorkCreatedV1 published" || true

echo "==> Logs Provider Matching"
kubectl -n hda logs deploy/provider-matching --tail=80 | grep -E "WorkCreatedV1 received|Matching processed" || true

fail=0
kubectl -n hda logs deploy/partner-integration --tail=200 | grep -q "EvaluatePartnerRulesV1 published: ${REF}" || fail=1
kubectl -n hda logs deploy/partner-rules --tail=200 | grep -q "EvaluatePartnerRulesV1 received: ${REF}" || fail=1
kubectl -n hda logs deploy/partner-rules --tail=200 | grep -q "PartnerRulesEvaluatedV1 published: ${REF}" || fail=1
kubectl -n hda logs deploy/work-orchestration -c work-orchestration --tail=200 | grep -q "PartnerRulesEvaluatedV1 received: ${REF}" || fail=1
kubectl -n hda logs deploy/work-orchestration -c work-orchestration --tail=200 | grep -q "Work persisted" || fail=1
kubectl -n hda logs deploy/work-orchestration -c work-orchestration --tail=200 | grep -q "WorkCreatedV1 published" || fail=1
kubectl -n hda logs deploy/provider-matching --tail=200 | grep -q "WorkCreatedV1 received" || fail=1
kubectl -n hda logs deploy/provider-matching --tail=200 | grep -q "Matching processed" || fail=1

if [[ "${fail}" -ne 0 ]]; then
  echo "ERROR: flujo E2E incompleto en GCP." >&2
  exit 1
fi

echo "==> Verify OK (flujo PI → PR → WO → PM)"
