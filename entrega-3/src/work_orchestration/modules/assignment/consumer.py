# Segundo módulo del servicio.
# Se comunica con Work exclusivamente mediante el evento WorkCreated.
import json, os, pika

def on_work_created(ch, method, properties, body):
    event = json.loads(body)
    print(f"[assignment] WorkCreated recibido: {event['work_id']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def run():
    connection = pika.BlockingConnection(
        pika.URLParameters(os.getenv("RABBITMQ_URL","amqp://guest:guest@localhost:5672/")))
    channel = connection.channel()
    channel.exchange_declare(exchange="hda.domain", exchange_type="topic", durable=True)
    channel.queue_declare(queue="assignment.work-created", durable=True)
    channel.queue_bind(exchange="hda.domain", queue="assignment.work-created",
                       routing_key="work.created")
    channel.basic_consume(queue="assignment.work-created", on_message_callback=on_work_created)
    channel.start_consuming()

if __name__ == "__main__": run()
