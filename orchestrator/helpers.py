from const import get_ENV
rabbitmq_url = get_ENV("RABBITMQ_URL")

from .types import Payload
import aio_pika 
import logging
import sys 
import json
import asyncio
import time



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

def serialize_event_obj(event: dict, resource: str) -> Payload:
    if not event:
        return {}

    event_type = event.get("type")
    obj = event.get("object")

    payload = {
        "name": obj.metadata.name if obj and obj.metadata else None,
        "type": event_type,
        "namespace": obj.metadata.namespace if obj and obj.metadata else None,
        "reason": event.get("reason")
            or next((cond.reason for cond in (getattr(obj.status, "conditions", []) or []) if cond.reason), None),
        "message": event.get("message")  or "",
        "timestamp": (event.get("lastTimestamp") or event.get("eventTime") or ""),
        "conditions": [
            {"type": cond.type, "status": cond.status, "reason": cond.reason}
            for cond in (getattr(obj.status, "conditions", []) or [])
        ],
    }

    payload["tier"] = classify_event(payload["reason"])

    return Payload(
        resource=resource,
        type=payload["type"],
        name=payload["name"],
        namespace=payload["namespace"],
        reason=payload["reason"],
        message=payload["message"],
        conditions=payload["conditions"],
        timestamp=payload["timestamp"],
        tier=payload["tier"],
    )


def classify_event(reason: str) -> str:
    if reason in ["CrashLoopBackOff", "OOMKilled", "ImagePullBackOff", "NodeNotReady"]:
        return "critical"
    elif reason in ["BackOff", "Unhealthy", "IngressBackendNotFound"]:
        return "important"
    else:
        return "informational"




async def connect_rabbitmq():
    """Keep trying to connect to RabbitMQ until success."""
    while True:
        try:
            connection = await aio_pika.connect_robust(rabbitmq_url)
            logger.info("Connected to RabbitMQ")
            return connection
        except Exception as e:
            logger.error(f"RabbitMQ connection failed: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)




async def process_event(channel: aio_pika.Channel, payload: Payload, exchange_name: str, resource_Name:str, to_be_processed_events:list):
    """Send event to RabbitMQ if relevant."""

    event_type = payload.type
    
    if event_type in to_be_processed_events:
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
        logger.info(f"Published. Resource: {resource_Name}, Event_Type: {event_type}")



async def stream_k8s_events(api_function, namespace: str, w):
    """Wrapper to turn blocking watch into async generator."""
    # w = watch.Watch()
    while True:
        try:
            for event in w.stream(api_function, namespace=namespace):
                yield event
        except Exception as e:
            logger.error(f"Watch failed: {e}, retrying in 5 seconds...")
            time.sleep(5)