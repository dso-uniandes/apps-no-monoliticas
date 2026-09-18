#!/usr/bin/env bash
set -euo pipefail

PI_URL="${PI_URL:-http://localhost:8001}"
WO_URL="${WO_URL:-http://localhost:8003}"

success_ref="saga-success-$(date +%s)"
fail_ref="saga-fail-$(date +%s)"

echo "==> Caso exitoso: ${success_ref}"
curl -fsS -X POST "${PI_URL}/partner-requests" \
  -H "Content-Type: application/json" \
  -d "{\"partner_id\":\"partner-demo\",\"payload\":{\"reference\":\"${success_ref}\",\"municipality\":\"Bogota\",\"country_code\":\"CO\",\"service_type\":\"HOME_REPAIR\"}}"
echo

echo "==> Caso con compensacion: ${fail_ref}"
curl -fsS -X POST "${PI_URL}/partner-requests" \
  -H "Content-Type: application/json" \
  -d "{\"partner_id\":\"partner-demo\",\"payload\":{\"reference\":\"${fail_ref}\",\"municipality\":\"Bogota\",\"country_code\":\"CO\",\"service_type\":\"HOME_REPAIR\"}}"
echo

echo "==> Esperando eventos async..."
sleep 12

echo "==> Saga Log exitoso"
curl -fsS "${WO_URL}/sagas/${success_ref}"
echo

echo "==> Saga Log compensado"
curl -fsS "${WO_URL}/sagas/${fail_ref}"
echo

echo "==> Logs utiles"
docker logs provider-matching --tail=120 | grep -E 'MatchingCompletedV1 published|MatchingFailedV1 published' || true
docker logs work-orchestration --tail=160 | grep -E 'MatchingFailedV1 received|WorkCancelledV1 published|WorkCreatedV1 published' || true
