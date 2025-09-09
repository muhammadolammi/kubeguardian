from const import get_ENV
rabbitmq_url = get_ENV("RABBITMQ_URL")
from typing import Any

from .types import Payload
import aio_pika 
import logging
import sys 
import json
import asyncio
import time
from kubernetes import watch



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

def classify_event(reason: str) -> str:
    if reason in ["CrashLoopBackOff", "OOMKilled", "ImagePullBackOff", "NodeNotReady"]:
        return "critical"
    elif reason in ["BackOff", "Unhealthy", "IngressBackendNotFound"]:
        return "important"
    else:
        return "informational"

def serialize_event_obj(event: dict[str, Any], resource: str) -> Payload | None:
    if not event:
        return None

    event_type = event.get("type")
    obj = event.get("object")

    if obj is None:
        return None

    # Try to extract metadata safely
    name = getattr(getattr(obj, "metadata", None), "name", None)
    namespace = getattr(getattr(obj, "metadata", None), "namespace", None)

    # Case 1: Kubernetes Event resource
    if getattr(obj, "kind", None) == "Event":
        payload_dict = {
            "name": getattr(obj.involved_object, "name", None),
            "type": event_type,
            "namespace": getattr(obj.involved_object, "namespace", None),
            "reason": getattr(obj, "reason", None),
            "message": getattr(obj, "message", ""),
            "timestamp": getattr(obj, "last_timestamp", None) or getattr(obj, "event_time", None),
            "conditions": [],
        }

    # Case 2: Workloads & cluster objects
    else:
        # Handle conditions defensively
        conditions = []
        if hasattr(obj, "status") and getattr(obj.status, "conditions", None):
            conditions = [
                {
                    "type": getattr(cond, "type", None),
                    "status": getattr(cond, "status", None),
                    "reason": getattr(cond, "reason", None),
                }
                for cond in obj.status.conditions
            ]

        payload_dict = {
            "name": name,
            "type": event_type,
            "namespace": namespace,   # may be None for cluster-scoped objects
            "reason": event.get("reason")
                or next(
                    (getattr(cond, "reason", None) for cond in conditions if getattr(cond, "reason", None)),
                    None,
                ),
            "message": event.get("message") or "",
            "timestamp": event.get("lastTimestamp") or event.get("eventTime") or None,
            "conditions": conditions,
        }

    # Add severity/tier classification
    payload_dict["tier"] = classify_event(payload_dict.get("reason"))

    # Build Pydantic Payload (namespace is optional now)
    return Payload(
        resource=resource,
        type=payload_dict["type"],
        name=payload_dict["name"],
        namespace=payload_dict.get("namespace"),
        reason=payload_dict.get("reason"),
        message=payload_dict.get("message"),
        conditions=payload_dict.get("conditions", []),
        timestamp=payload_dict.get("timestamp"),
        tier=payload_dict.get("tier"),
    )

async def connect_rabbitmq():
    """Keep trying to connect to RabbitMQ until success."""
    while True:
        try:
            connection = await aio_pika.connect_robust(rabbitmq_url)
            logger.info("Connected to RabbitMQ")
            channel = await connection.channel()

            return connection, channel
        except Exception as e:
            logger.error(f"RabbitMQ connection failed: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)




async def process_event(channel: aio_pika.Channel, payload: Payload, exchange_name: str, resource_Name:str, to_be_processed_events:list):
    """Send event to RabbitMQ if relevant."""

    event_type = payload.type 

    
    if event_type in to_be_processed_events or any(
    reason and reason in payload.reason for reason in to_be_processed_events if payload.reason):
        message_body = payload.model_dump_json().encode()
        event_key = event_type if event_type in to_be_processed_events else payload.reason
        namespace = payload.namespace or "cluster"
        routing_key = f"{namespace}.{resource_Name}.{event_key.lower()}"
        exchange = await channel.get_exchange(exchange_name)
        await exchange.publish(
            aio_pika.Message(
                body=message_body,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=routing_key,
        )
        reason_str = f"/{payload.reason}" if payload.reason else ""

        logger.info(f"Published {resource_Name} {payload.type}:{reason_str} for {payload.name}")

async def stream_k8s_events(api_function, namespace: str):
    w = watch.Watch()

    def sync_stream():
        if namespace:
            yield from w.stream(api_function, namespace=namespace, timeout_seconds=30)
        else:
            yield from w.stream(api_function, timeout_seconds=30)

    while True:
        try:
            # run the sync generator in a background thread
            iterator = sync_stream()
            while True:
                try:
                    event = await asyncio.to_thread(lambda: next(iterator))
                    yield event
                except StopIteration:
                    break
        except Exception as e:
            logger.error(f"Watch failed: {e}, retrying in 5s...")
            await asyncio.sleep(5)
        finally:
            w.stop()
