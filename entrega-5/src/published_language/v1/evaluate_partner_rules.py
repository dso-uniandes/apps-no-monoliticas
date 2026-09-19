from pulsar.schema import Long, Record, String


class EvaluatePartnerRulesV1(Record):
    command_id = String()
    occurred_at = Long()
    schema_version = String(default='1')
    partner_id = String()
    external_reference = String()
    city = String()
    country = String()
    service_type = String()
