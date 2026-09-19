#!/usr/bin/env bash
set -euo pipefail

# Demo de la SAGA coreografiada a traves del BFF: una transaccion exitosa y una
# con fallo que dispara compensacion. Todo se consulta por la misma API.
BFF_URL="${BFF_URL:-http://localhost:8005}"

success_ref="saga-success-$(date +%s)"
fail_ref="saga-fail-$(date +%s)"

post_request() {
  curl -fsS -X POST "${BFF_URL}/api/v1/partner-requests" \
    -H "Content-Type: application/json" \
    -d "{\"partner_id\":\"partner-demo\",\"payload\":{\"reference\":\"$1\",\"municipality\":\"Bogota\",\"country_code\":\"CO\",\"service_type\":\"HOME_REPAIR\"}}"
  echo
}

show_status() {
  curl -fsS "${BFF_URL}/api/v1/partner-requests/$1" | python3 -m json.tool
}

echo "==> Health agregado"
curl -fsS "${BFF_URL}/api/v1/health" | python3 -m json.tool

echo "==> Caso exitoso: ${success_ref}"
post_request "${success_ref}"

echo "==> Caso con compensacion: ${fail_ref}"
post_request "${fail_ref}"

echo "==> Esperando eventos async..."
sleep 12

echo "==> Estado de la SAGA exitosa (esperado: COMPLETED)"
show_status "${success_ref}"

echo "==> Estado de la SAGA compensada (esperado: COMPENSATED)"
show_status "${fail_ref}"

echo "==> Logs utiles"
docker logs provider-matching --tail=120 | grep -E 'MatchingCompletedV1 published|MatchingFailedV1 published' || true
docker logs work-orchestration --tail=160 | grep -E 'MatchingFailedV1 received|WorkCancelledV1 published|WorkCreatedV1 published' || true
