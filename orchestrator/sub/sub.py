from ..const import  exchange_name
from const import get_ENV
AI_AGENT_URL = get_ENV("AI_AGENT_URL")
import logging 
import sys
from aio_pika import Message



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)
from typing import List
import asyncio
import json
import os
import sys
import aio_pika
from session.session import create_new_session, delete_session
from google.adk.sessions import DatabaseSessionService

import httpx 
from ..helpers import connect_rabbitmq
from ..types import Payload
RESOURCE_EVENTS_MAP = {
    "Deployment": ["ERROR", "DELETED", "WARNING"],
    "Pod": ["ERROR", "FAILED", "DELETED", "WARNING", "OOMKilled", "CrashLoopBackOff", "Completed"],
    "ReplicaSet": ["ERROR", "FAILED", "DELETED", "WARNING", 'ScalingReplicaSet'],
    "Node": ["Ready" , "NotReady", "MemoryPressure","DiskPressure", "NetworkUnavailable", "KubeletReady"],
    "Service": ["ERROR", "DELETED", "WARNING", "LoadBalancerUpdate","ClusterIPAllocationFailure"],
    "Ingress": ["ERROR", "DELETED", "WARNING","ReconcileFailed","SyncFailed","CertificateError"],
    "ConfigMap": ["CREATED", "UPDATED", "DELETED", "ERROR"],
    "Secret": ["CREATED", "UPDATED", "DELETED", "ERROR"],
    "PersistentVolume": ["Bound", "Unbound", "Released", "Failed", "Deleted"],
    "PersistentVolumeClaim": ["Bound", "Unbound", "Released", "Failed", "Deleted"],
    }   

MAX_AGENT_RETRIES = 3
MAX_RABBITMQ_RETRIES = 2

# Batching config
BATCH_INTERVAL = 60  # seconds
BATCH_SIZE = 20         # max events per batch


buffer = []  # shared event buffer
def format_payloads_for_ai(payloads: List[Payload]) -> str:
    """
    Convert a list of Payload objects into a readable string for the AI agent.
    """
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
    """Send current batch to AI agent, with retries + RabbitMQ fallback."""
    message = format_payloads_for_ai(data)
    payload = {
        "agent_type": "remediator",
        "namespace": namespace,
        "session_id": session.id,
        "user_id": session.user_id,
        "message": message,
    }

    async with httpx.AsyncClient() as client:
        tries = 0
        while tries < MAX_AGENT_RETRIES:
            try:
                resp = await client.post(
                    f"{AI_AGENT_URL}/run-agent",
                    json=payload,
                    timeout=60,
                )
                resp.raise_for_status()
                data = resp.json()
                agent_response: str = data.get("response", "")

                if agent_response.startswith("⚠️ Agent failed"):
                    tries += 1
                    await asyncio.sleep(2**tries)  # exponential backoff
                    continue

                # ✅ Success
                logger.info(f"[AI Response] {agent_response}")
                return agent_response

            except httpx.HTTPStatusError as e:
                status = e.response.status_code
                if status == 429:  # Quota exceeded
                    tries += 1
                    sleep_time = 2**tries
                    logger.warning(
                        f"Quota error (429). Sleeping {sleep_time}s before retry..."
                    )
                    await asyncio.sleep(sleep_time)
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

    # ❌ All retries failed — republish to RabbitMQ
    if retry_count < MAX_RABBITMQ_RETRIES:
        logger.warning("All retries failed. Republishing to RabbitMQ...")
        exchange = await channel.declare_exchange(
            exchange_name, aio_pika.ExchangeType.TOPIC, passive=True
        )
        await exchange.publish(
            Message(
                body=json.dumps([p.model_dump() for p in data]).encode(),
                headers={"x-retry-count": retry_count + 1},
            ),
            routing_key=f"{namespace}.ai.retry",
        )
    else:
        logger.error(f"Event permanently failed after retries: {payload}")
        # TODO: insert into failure_db.save(payload)


async def flush_buffer(
    namespace: str, session: DatabaseSessionService, channel
):
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


async def periodic_flusher(
    namespace: str, session: DatabaseSessionService, channel
):
    """Background task to flush buffer every BATCH_INTERVAL seconds."""
    await asyncio.sleep(BATCH_INTERVAL)
    await flush_buffer(namespace, session, channel)


async def sub(namespace: str, queue, session: DatabaseSessionService, channel):
    """Async subscriber that listens for deployment events and forwards them to AI agent."""
    asyncio.create_task(periodic_flusher(namespace, session, channel))

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():  # auto-ack if no exception
                try:
                    payload = json.loads(message.body.decode())
                    retry_count = message.headers.get("x-retry-count", 0)

                    logger.info(
                        f"Received event for AI. "
                        f"Resource: {payload['resource']}, "
                        f"Event_Type: {payload['type']}, "
                        f"Namespace: {payload['namespace']}, "
                        f"Retry: {retry_count}"
                    )

                    buffer.append(Payload(**payload))

                    # Flush immediately if resource is deleted
                    if payload["type"] == "DELETED":
                        await flush_buffer(namespace, session, channel)

                    # Flush if buffer is too big
                    if len(buffer) >= BATCH_SIZE:
                        await flush_buffer(namespace, session, channel)

                except Exception as e:
                    logger.error(f"Failed to process message: {e}")

                    if retry_count < MAX_RABBITMQ_RETRIES:
                        exchange = await channel.declare_exchange(
                            exchange_name, aio_pika.ExchangeType.TOPIC
                        )
                        await exchange.publish(
                            Message(
                                body=message.body,
                                headers={"x-retry-count": retry_count + 1},
                            ),
                            routing_key=f"{namespace}.ai.retry",
                        )
                        logger.warning(
                            f"Republished failed message with retry {retry_count+1}"
                        )
                    else:
                        logger.error(
                            f"Message permanently failed after {retry_count} retries: {message.body.decode()}"
                        )
                        # TODO: Insert into failure_db.save(payload)

async def async_main():
    try:
        session = await create_new_session("remediator")
        authorized_namespace = "default"
        connection, channel = await connect_rabbitmq()
        exchange = await channel.declare_exchange(exchange_name, aio_pika.ExchangeType.TOPIC, passive=True)

        # Queue to capture ALL events (use wildcards)
        queue = await channel.declare_queue("ai_agent_queue", durable=True)
        #Bind everything on our namespace
        await queue.bind(exchange, routing_key=f"{authorized_namespace}.*.*")  # "#" = match everything
        #Bind cluster wide logs
        await queue.bind(exchange, routing_key=f"cluster.*.*")

        await sub(authorized_namespace, queue, session, channel )
    finally:
        #Delete session
        await delete_session(session_id=session.id, user_id=session.user_id, app_name=session.app_name)

        # Close connections
        await channel.close()
        await connection.close()

if __name__ == '__main__':
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
