from const import get_ENV
from type import Payload
import aio_pika 
import logging
from datetime import datetime
import sys 
import asyncio
from kubernetes import watch
from typing import Any

rabbitmq_url = get_ENV("RABBITMQ_URL")




logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)
def classify_event(reason: str | None, event_type: str | None = None) -> str:
    """
    Classify an event severity based on reason and optionally event_type.
    """
    if not reason:
        # Handle special case: deleted events
        if event_type and event_type.lower() == "deleted":
            return "important"
        return "informational"

    critical_reasons = {"CrashLoopBackOff", "OOMKilled", "ImagePullBackOff", "NodeNotReady"}
    important_reasons = {"BackOff", "Unhealthy", "IngressBackendNotFound"}

    if reason in critical_reasons:
        return "critical"
    elif reason in important_reasons:
        return "important"
    return "informational"


def format_timestamp(ts: Any) -> str | None:
    """Convert timestamp object to ISO 8601 string if possible."""
    if ts is None:
        return None
    if isinstance(ts, str):
        return ts  # already a string
    if isinstance(ts, datetime):
        return ts.isoformat()
    try:
        return datetime.fromisoformat(str(ts)).isoformat()
    except Exception:
        return str(ts)  # fallback to string

def serialize_event_obj(event: dict[str, Any], resource: str) -> Payload | None:
    if not event:
        return None

    event_type = event.get("type")
    obj = event.get("object")
    if obj is None:
        return None

    kind = getattr(obj, "kind", None)
    metadata = getattr(obj, "metadata", None)

    # Safe metadata extraction
    name = getattr(metadata, "name", None)
    namespace = getattr(metadata, "namespace", None)
    labels = getattr(metadata, "labels", {}) or {}
    annotations = getattr(metadata, "annotations", {}) or {}

    # Case 1: Kubernetes Event
    if kind == "Event":
        ts = getattr(obj, "last_timestamp", None) or getattr(obj, "event_time", None)
        payload_dict = {
            "name": getattr(obj.involved_object, "name", None),
            "type": event_type,
            "namespace": getattr(obj.involved_object, "namespace", None),
            "reason": getattr(obj, "reason", None),
            "message": getattr(obj, "message", ""),
            "timestamp": format_timestamp(ts),
            "conditions": [],
        }

    # Case 2: Workloads, Configs, Networking
    else:
        # Extract conditions if present
        conditions = []
        status_obj = getattr(obj, "status", None)
        if status_obj and getattr(status_obj, "conditions", None):
            conditions = [
                {
                    "type": getattr(cond, "type", None),
                    "status": getattr(cond, "status", None),
                    "reason": getattr(cond, "reason", None),
                }
                for cond in status_obj.conditions
            ]

        reason = event.get("reason") or next(
            (getattr(cond, "reason", None) for cond in conditions if getattr(cond, "reason", None)),
            None,
        )

        message = event.get("message") or ""

        # Special handling by kind
        extra_info = {}
        if kind == "Pod":
            spec = getattr(obj, "spec", None)
            if spec:
                containers = [
                    {"name": getattr(c, "name", None), "image": getattr(c, "image", None)}
                    for c in getattr(spec, "containers", [])
                ]
                extra_info["containers"] = containers
        elif kind == "Deployment":
            spec = getattr(obj, "spec", None)
            status = getattr(obj, "status", None)
            if spec and status:
                extra_info["replicas"] = {
                    "desired": getattr(spec, "replicas", None),
                    "available": getattr(status, "available_replicas", None),
                    "updated": getattr(status, "updated_replicas", None),
                }
        elif kind == "Service":
            spec = getattr(obj, "spec", None)
            if spec:
                extra_info["type"] = getattr(spec, "type", None)
                extra_info["ports"] = [
                    {
                        "port": getattr(p, "port", None),
                        "targetPort": getattr(p, "target_port", None),
                        "protocol": getattr(p, "protocol", None),
                    }
                    for p in getattr(spec, "ports", [])
                ]
        elif kind == "Node":
            status = getattr(obj, "status", None)
            if status:
                extra_info["capacity"] = getattr(status, "capacity", {})
                extra_info["allocatable"] = getattr(status, "allocatable", {})
        elif kind == "ConfigMap":
            data = getattr(obj, "data", None)
            if data:
                extra_info["data_keys"] = list(data.keys())
        elif kind == "Ingress":
            spec = getattr(obj, "spec", None)
            status = getattr(obj, "status", None)
            if spec:
                rules = [
                    {
                        "host": getattr(r, "host", None),
                        "paths": [
                            getattr(p, "path", None)
                            for p in getattr(getattr(r, "http", None), "paths", []) or []
                        ],
                    }
                    for r in getattr(spec, "rules", []) or []
                ]
                extra_info["rules"] = rules
            if status:
                extra_info["load_balancer"] = getattr(status, "load_balancer", None)

        ts = getattr(obj, "last_timestamp", None) or getattr(obj, "event_time", None) or getattr(metadata, "creation_timestamp", None)
        payload_dict = {
            "name": name,
            "type": event_type,
            "namespace": namespace,
            "reason": reason,
            "message": message,
            "timestamp": format_timestamp(ts),
            "conditions": conditions,
            "labels": labels,
            "annotations": annotations,
            "extra": extra_info,
        }

    # Add severity/tier classification
    payload_dict["tier"] = classify_event(payload_dict.get("reason"), event_type)

    # Build Payload (Pydantic)
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
        labels=payload_dict.get("labels", {}),
        annotations=payload_dict.get("annotations", {}),
        extra=payload_dict.get("extra", {}),
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

async def stream_k8s_events(api_function, namespace: str | None):
    w = watch.Watch()

    def sync_stream():
        if namespace:
            yield from w.stream(api_function, namespace=namespace, timeout_seconds=30)
        else:
            yield from w.stream(api_function, timeout_seconds=30)

    def safe_next(it):
        try:
            return next(it)
        except StopIteration:
            return None

    while True:
        try:
            iterator = sync_stream()
            while True:
                event = await asyncio.to_thread(safe_next, iterator)
                if event is None:  # iterator exhausted
                    break
                yield event
        except Exception as e:
            logger.error(f"Watch failed: {e}, retrying in 5s...")
            await asyncio.sleep(5)
        finally:
            w.stop()