from partner_integration.aplicacion.puertos.payload_adapter import AdaptedPartnerPayload
from partner_integration.dominio.excepciones import PartnerRequestInvalido


class PartnerDemoPayloadAdapter:
    """ACL mínimo para el partner B2B2C partner-demo."""

    def adapt(self, raw_payload: dict) -> AdaptedPartnerPayload:
        reference = (raw_payload or {}).get('reference')
        municipality = (raw_payload or {}).get('municipality')
        country_code = (raw_payload or {}).get('country_code')
        service_type = (raw_payload or {}).get('service_type')

        if not reference:
            raise PartnerRequestInvalido('partner-demo requiere reference')
        if not municipality or not country_code:
            raise PartnerRequestInvalido('partner-demo requiere municipality y country_code')

        return AdaptedPartnerPayload(
            external_reference=str(reference),
            canonical_payload={
                'city': str(municipality),
                'country': str(country_code),
                'service_type': str(service_type) if service_type else None,
            },
        )
