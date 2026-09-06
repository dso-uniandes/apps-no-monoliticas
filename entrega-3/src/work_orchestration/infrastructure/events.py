import json, os
from dataclasses import asdict
from datetime import datetime
from uuid import UUID
import pika
from work_orchestration.domain.ports import EventPublisher

def _json_default(v):
    if isinstance(v, (UUID, datetime)): return str(v)
    raise TypeError()

class RabbitEventPublisher(EventPublisher):
    def __init__(self):
        self.url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

    def publish(self, event) -> None:
        connection = pika.BlockingConnection(pika.URLParameters(self.url))
        channel = connection.channel()
        channel.exchange_declare(exchange="hda.domain", exchange_type="topic", durable=True)
        body = json.dumps(asdict(event), default=_json_default).encode()
        channel.basic_publish(exchange="hda.domain", routing_key="work.created", body=body,
                              properties=pika.BasicProperties(
                                  delivery_mode=2,
                                  content_type="application/json",
                                  message_id=str(event.event_id)))
        connection.close()
