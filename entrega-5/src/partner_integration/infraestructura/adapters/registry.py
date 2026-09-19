from partner_integration.aplicacion.puertos.payload_adapter import PartnerPayloadAdapter
from partner_integration.infraestructura.adapters.partner_demo_payload_adapter import (
    PartnerDemoPayloadAdapter,
)


def get_payload_adapters() -> dict[str, PartnerPayloadAdapter]:
    return {
        'partner-demo': PartnerDemoPayloadAdapter(),
    }
