from ..const import  exchange_name
from const import get_ENV
AI_AGENT_URL = get_ENV("AI_AGENT_URL")
import logging 
import sys

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
from session.session import create_new_session, delete_session_by_user_id, get_session_by_user_id
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

async def send_events_to_Agent(namespace:str, data:List[Payload]):
    """Send current bacth to AI."""
    message = format_payloads_for_ai(data)
    session =await get_session_by_user_id("remediator")
    payload = {
        "agent_type": "remediator",
        "namespace": namespace,
        "user_id": "remediator",
        "session_id": session.id,
        "message": message  # send full message as text
    }

    # Send to AI agent service
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(AI_AGENT_URL, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            agent_response = data.get("response")
            return agent_response
        except httpx.HTTPError as e:
            print(f"[!] Failed to call AI agent: {e}")
            return f"⚠️ AI agent call failed: {str(e)}"
    


async def flush_buffer(namespace:str):
    """Flush buffered events to AI agent."""
    global buffer
    if not buffer:
        return
    try:
        batch = buffer.copy()
        buffer.clear()
        # 🔑 Forward the batch to AI agent here
        logger.info(f"Sending batch of {len(batch)} events to AI")
        agent_response=await send_events_to_Agent(namespace,batch)
        print(f"[AI Response] {agent_response}")

    except Exception as e:
        logger.error(f"Failed to flush buffer: {e}")


async def periodic_flusher(namespace:str):
    """Background task to flush buffer every BATCH_INTERVAL seconds."""
    while True:
        await asyncio.sleep(BATCH_INTERVAL)
        # SEssion should only last long for that time, we specified, we can delete the session here and recreate
        delete_session_by_user_id("remediator")
        await create_new_session("remediator")
        await flush_buffer(namespace)

async def sub( namespace: str, channel):
    """Async subscriber that listens for deployment events."""
    exchange = await channel.declare_exchange(exchange_name, aio_pika.ExchangeType.TOPIC)

    # Queue to capture ALL events (use wildcards)
    queue = await channel.declare_queue("ai_agent_queue", durable=True)
    #Bind everything on our namespace
    await queue.bind(exchange, routing_key=f"{namespace}.*.*")  # "#" = match everything
    #Bind cluster wide logs
    await queue.bind(exchange, routing_key=f"cluster.*.*")

    # Start background flusher
    asyncio.create_task(periodic_flusher(namespace))
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():  # auto-ack if no exception
                try:
                    payload = json.loads(message.body.decode())
                    # 🔑 Forward payload to AI agent here
                    logger.info(f"Received event for AI: {payload}")
                    buffer.append(Payload(**payload))
                    # Flush immediately if buffer too big
                    if len(buffer) >= BATCH_SIZE:
                        await flush_buffer(namespace)
                except Exception as e:
                    logger.error(f"Failed to process message: {e}")
                    # we can republish the messages here and retry for x-time
                    #message.nack(requeue=True) 

async def async_main():
    try:
        await create_new_session("remediator")
        authorized_namespace = "default"
        connection, channel = await connect_rabbitmq()
        await sub(
            authorized_namespace, channel
        )
    finally:
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
