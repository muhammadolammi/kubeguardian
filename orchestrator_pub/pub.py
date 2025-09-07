import asyncio
import json
import logging
import sys
import time
from kubernetes import client, config, watch
import aio_pika
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

EVENTS = ["ERROR", "DELETED", "WARNING"]


async def connect_rabbitmq():
    """Keep trying to connect to RabbitMQ until success."""
    while True:
        try:
            connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq:5672/")
            logger.info("Connected to RabbitMQ")
            return connection
        except Exception as e:
            logger.error(f"RabbitMQ connection failed: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)

def serialize_deployment(deploy_obj: client.V1Deployment) -> dict:
    if not deploy_obj:
        return {}

    return {
        "name": deploy_obj.metadata.name if deploy_obj.metadata else None,
        "namespace": deploy_obj.metadata.namespace if deploy_obj.metadata else None,
        "replicas": deploy_obj.spec.replicas if deploy_obj.spec else None,
        "available_replicas": deploy_obj.status.available_replicas if deploy_obj.status else None,
        "conditions": [
            {"type": cond.type, "status": cond.status, "reason": cond.reason}
            for cond in deploy_obj.status.conditions
        ] if deploy_obj.status and deploy_obj.status.conditions else []
    }

async def process_event(channel: aio_pika.Channel, event: any, exchange_name: str):
    """Send event to RabbitMQ if relevant."""
    event_type = event.get("type")
    deploy_obj: client.V1Deployment = event.get("object")
    payload = serialize_deployment(deploy_obj)
    payload["type"] =event_type
  

    if event_type in EVENTS:
        routing_key = event_type
        message_body = json.dumps(payload).encode()


        exchange = await channel.get_exchange(exchange_name)
        await exchange.publish(
            aio_pika.Message(
                body=message_body,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=routing_key,
        )
        logger.info(f"Published: {event_type}")


async def deployment_pub(namespace: str):
    """Watch Kubernetes deployments and publish events forever."""
    # Load kube config
    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()  #

    apps_v1 = client.AppsV1Api()
    w = watch.Watch()

    while True:
        try:
            connection = await connect_rabbitmq()
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=1)

            exchange_name = f"{namespace}_deployments"
            # exchange = await channel.declare_exchange(
            #     exchange_name, aio_pika.ExchangeType.DIRECT, durable=True
            # )
            await channel.declare_exchange(
                exchange_name, aio_pika.ExchangeType.DIRECT, durable=True
            )

            logger.info("Starting Kubernetes watch...")
            async for event in stream_k8s_events(apps_v1, namespace):
                await process_event(channel, event, exchange_name)
        except Exception as e:
            logger.error(f"Publisher error: {e}, retrying in 5 seconds...")
            await asyncio.sleep(5)


async def stream_k8s_events(api, namespace: str):
    """Wrapper to turn blocking watch into async generator."""
    w = watch.Watch()
    while True:
        try:
            for event in w.stream(api.list_namespaced_deployment, namespace=namespace):
                yield event
        except Exception as e:
            logger.error(f"Watch failed: {e}, retrying in 5 seconds...")
            time.sleep(5)


async def main():
    authorized_namespace = "bank-of-anthos"
    await deployment_pub(authorized_namespace)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted")
        sys.exit(0)
