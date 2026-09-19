from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class AdaptedPartnerPayload:
    external_reference: str
    canonical_payload: dict


class PartnerPayloadAdapter(Protocol):
    def adapt(self, raw_payload: dict) -> AdaptedPartnerPayload:
        ...
