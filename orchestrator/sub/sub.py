from ..const import exchange_name
from const import get_ENV

AI_AGENT_URL = get_ENV("AI_AGENT_URL")
authorized_namespace = get_ENV("AUTHORIZED_NAMESPACE")

import logging
import sys
import asyncio
import json
from typing import List
import aio_pika
import httpx

from session.session import create_new_session, delete_session
from google.adk.sessions import DatabaseSessionService
from ..helpers import connect_rabbitmq
from ..types import Payload

# ------------------ Logging ------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

# ------------------ Config ------------------
RESOURCE_EVENTS_MAP = {
    "Deployment": ["ERROR", "DELETED", "WARNING"],
    "Pod": ["ERROR", "FAILED", "DELETED", "WARNING", "OOMKilled", "CrashLoopBackOff", "Completed"],
    "ReplicaSet": ["ERROR", "FAILED", "DELETED", "WARNING", 'ScalingReplicaSet'],
    "Node": ["Ready", "NotReady", "MemoryPressure", "DiskPressure", "NetworkUnavailable", "KubeletReady"],
    "Service": ["ERROR", "DELETED", "WARNING", "LoadBalancerUpdate", "ClusterIPAllocationFailure"],
    "Ingress": ["ERROR", "DELETED", "WARNING", "ReconcileFailed", "SyncFailed", "CertificateError"],
    "ConfigMap": ["CREATED", "UPDATED", "DELETED", "ERROR"],
    "Secret": ["CREATED", "UPDATED", "DELETED", "ERROR"],
    "PersistentVolume": ["Bound", "Unbound", "Released", "Failed", "Deleted"],
    "PersistentVolumeClaim": ["Bound", "Unbound", "Released", "Failed", "Deleted"],
}

MAX_AGENT_RETRIES = 3
MAX_RABBITMQ_RETRIES = 2
BATCH_SIZE = 20

buffer: List[Payload] = []  # shared event buffer

# ------------------ Helper Functions ------------------
def format_payloads_for_ai(payloads: List[Payload]) -> str:
    if not payloads:
        return "No new events to process."

    messages = []
    for i, p in enumerate(payloads, start=1):
        msg = (
            f"[{i}] Resource: {p.resource}\n"
            f"   Name: {p.name}\n"
            f"   Namespace: {p.namespace or 'N/A'}\n"
            f"   Type: {p.type}\n"
            f"   Reason: {p.reason or 'N/A'}\n"
            f"   Message: {p.message or 'N/A'}\n"
            f"   Tier: {p.tier or 'N/A'}\n"
            f"   Timestamp: {p.timestamp or 'N/A'}\n"
        )
        messages.append(msg)
    return "\n".join(messages)

async def send_events_to_agent(
    namespace: str,
    data: List[Payload],
    session: DatabaseSessionService,
    channel,
    retry_count: int = 0,
):
    """Send batch to AI agent, with retries + RabbitMQ fallback."""
    message_text = format_payloads_for_ai(data)
    payload = {
        "agent_type": "remediator",
        "session_id": session.id,
        "user_id": session.user_id,
        "message": message_text,
    }

    async with httpx.AsyncClient() as client:
        tries = 0
        while tries < MAX_AGENT_RETRIES:
            try:
                resp = await client.post(f"{AI_AGENT_URL}/run-agent", json=payload, timeout=60)
                resp.raise_for_status()
                data_resp = resp.json()
                agent_response: str = data_resp.get("response", "")
                if agent_response.startswith("⚠️ Agent failed"):
                    logger.info(f"{agent_response}")
                    logger.info(f"Retrying after agent failed.....")

                    tries += 1
                    await asyncio.sleep(2**tries)
                    continue
                logger.info(f"[AI Response] {agent_response}")
                return agent_response
            except httpx.HTTPStatusError as e:
                status = e.response.status_code
                if status == 429:
                    tries += 1
                    await asyncio.sleep(2**tries)
                    continue
                elif 500 <= status < 600:
                    tries += 1
                    await asyncio.sleep(2**tries)
                    continue
                else:
                    logger.error(f"Unrecoverable HTTP error: {e}")
                    break
            except httpx.HTTPError as e:
                logger.error(f"Transport error: {e}")
                tries += 1
                await asyncio.sleep(2**tries)

    # Republish to RabbitMQ if all retries fail
    if retry_count < MAX_RABBITMQ_RETRIES:
        logger.warning("All retries failed. Republishing to RabbitMQ...")
        exchange = await channel.declare_exchange(exchange_name, aio_pika.ExchangeType.TOPIC, durable=True)
        safe_payloads = [p.model_dump() if hasattr(p, "model_dump") else p for p in data]
        await exchange.publish(
            aio_pika.Message(
                body=json.dumps(safe_payloads).encode(),
                headers={"x-retry-count": retry_count + 1},
            ),
            routing_key=f"{namespace}.ai.retry",
        )
    else:
        logger.error(f"Event permanently failed after retries: {payload}")

async def flush_buffer(namespace: str, session: DatabaseSessionService, channel):
    """Flush buffered events to AI agent."""
    global buffer
    if not buffer:
        return
    try:
        batch = buffer.copy()
        buffer.clear()
        logger.info(f"Sending batch of {len(batch)} events to AI")
        await send_events_to_agent(namespace, batch, session, channel)
    except Exception as e:
        logger.error(f"Failed to flush buffer: {e}")

# ------------------ Subscriber ------------------
async def sub(namespace: str, queue, session: DatabaseSessionService, channel):
    """Async subscriber for deployment events."""
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                try:
                    payload_data = json.loads(message.body.decode())
                    retry_count = message.headers.get("x-retry-count", 0)

                    # Handle single dict or list of dicts
                    payload_objects: List[Payload] = []
                    if isinstance(payload_data, list):
                        for item in payload_data:
                            payload_objects.append(Payload(**item))
                    else:
                        payload_objects.append(Payload(**payload_data))

                    for payload_obj in payload_objects:
                        logger.info(
                            f"Received event for AI. "
                            f"Resource: {payload_obj.resource}, "
                            f"Event_Type: {payload_obj.type}, "
                            f"Namespace: {payload_obj.namespace}, "
                            f"Retry: {retry_count}"
                        )
                        buffer.append(payload_obj)

                        # Flush immediately if Deployment DELETED
                        if payload_obj.type == "DELETED" and payload_obj.resource == "Deployment":
                            await flush_buffer(namespace, session, channel)

                    # Flush if buffer too big
                    if len(buffer) >= BATCH_SIZE:
                        await flush_buffer(namespace, session, channel)

                except Exception as e:
                    logger.error(f"Failed to process message: {e}")
                    # Republish with retry
                    if retry_count < MAX_RABBITMQ_RETRIES:
                        exchange = await channel.declare_exchange(exchange_name, aio_pika.ExchangeType.TOPIC, durable=True)
                        await exchange.publish(
                            aio_pika.Message(
                                body=message.body,
                                headers={"x-retry-count": retry_count + 1},
                            ),
                            routing_key=f"{namespace}.ai.retry",
                        )
                        logger.warning(f"Republished failed message with retry {retry_count+1}")
                    else:
                        logger.error(f"Message permanently failed after {retry_count} retries: {message.body.decode()}")

# ------------------ Main ------------------
async def async_main():
    session = None
    connection = None
    channel = None
    try:
        session = await create_new_session("remediator")
        connection, channel = await connect_rabbitmq()
        exchange = await channel.declare_exchange(exchange_name, aio_pika.ExchangeType.TOPIC, durable=True)

        queue = await channel.declare_queue("ai_agent_queue", durable=True)
        await queue.bind(exchange, routing_key=f"{authorized_namespace}.*.*")
        await queue.bind(exchange, routing_key=f"cluster.*.*")

        await sub(authorized_namespace, queue, session, channel)
    finally:
        if session:
            await delete_session(session_id=session.id, user_id=session.user_id, app_name=session.app_name)
        if channel:
            await channel.close()
        if connection:
            await connection.close()

if __name__ == "__main__":
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("Interrupted")
        sys.exit(0)
