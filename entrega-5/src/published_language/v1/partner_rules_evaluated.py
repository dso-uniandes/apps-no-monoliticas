from pulsar.schema import Boolean, Long, Record, String


class PartnerRulesEvaluatedV1(Record):
    event_id = String()
    occurred_at = Long()
    schema_version = String(default='1')
    partner_id = String()
    external_reference = String()
    city = String()
    country = String()
    service_type = String()
    allowed = Boolean()
