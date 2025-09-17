from ..const import exchange_name
from const import get_ENV

AI_AGENT_URL = get_ENV("AI_AGENT_URL")
authorized_namespace = get_ENV("AUTHORIZED_NAMESPACE")
DB_URL = get_ENV("DB_URL")
CRYPT_KEY = get_ENV("CRYPT_KEY")

import httpx
import uuid
from fastapi import HTTPException

import logging
import sys
import asyncio
import json
from typing import List
import aio_pika
from google.adk.sessions import DatabaseSessionService
from ..helpers import connect_rabbitmq
from ..types import Payload
from helpers import AlertDB
alertdb = AlertDB(db_url=DB_URL,crypt_key=CRYPT_KEY)

# ------------------ Logging ------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

# ------------------ Config ------------------
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
    data: List[Payload],
    session: DatabaseSessionService,
):
    """Send batch to AI agent (no retries)."""
    message_text = format_payloads_for_ai(data)
    payload = {
        "appName": "remediator",
        "session_id": session["id"],
        "userId": session["userId"],
        "newMessage": {
            "parts": [{"text": message_text}],
            "role": "user",
        },
    }

    async with httpx.AsyncClient() as client:
        retries = 0
        max_retries=3
        while retries < max_retries:
            try:
                resp = await client.post(f"{AI_AGENT_URL}/run", json=payload, timeout=60)
                resp.raise_for_status()
                data = resp.json()
                #  print(data[0]["content"]["parts"][0]["text"])
                final_response_text :str= data[0]["content"]["parts"][0]["text"]
                logss = f"✅ Remediation Successful. [AI Response] {final_response_text}"
                logger.info(f"✅ Remediation Successful. [AI Response] {final_response_text}")
                alertdb.update_alert(logss, session_id=session.id)

                return 
            except Exception as e :
                logger.warning(
                    f"Error Encountered.error: {e}, Retry {retries+1}/{max_retries}. "
                    f"Sleeping for 30s before retry..."
                )
                retries += 1
                if retries > max_retries:
                    logger.error("Max retries reached. Dropping message or saving to DB.")
                    # TODO: Replace with actual DB persistence
                    logss = f"❌ ERROR Max retries reached. Last response: {final_response_text}. message: {message_text}, Last error: {e}"
                    alertdb.update_alert(logss, session_id=session.id)

                    #save_failed_request_to_db(payload)
                    return None 
                await asyncio.sleep(30)



async def flush_buffer(namespace: str, session: DatabaseSessionService, channel):
    """Flush buffered events to AI agent."""
    global buffer
    if not buffer:
        return
    try:
        batch = buffer.copy()
        buffer.clear()
        logger.info(f"Sending batch of {len(batch)} events to AI")
        await send_events_to_agent(batch, session)
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
                            f"Namespace: {payload_obj.namespace}"
                        )
                        buffer.append(payload_obj)

                        # Flush immediately if Deployment DELETED
                        if (
                            payload_obj.type == "DELETED"
                            and payload_obj.resource == "Deployment"
                        ):
                            await flush_buffer(namespace, session, channel)

                    # Flush if buffer too big
                    if len(buffer) >= BATCH_SIZE:
                        await flush_buffer(namespace, session, channel)

                except Exception as e:
                    logger.error(f"Failed to process message: {e}")
                    # Reject message without retry
                    await message.reject(requeue=False)


# ------------------ Main ------------------
async def async_main():
    session = None
    connection = None
    channel = None
    try:
        async with httpx.AsyncClient() as client:
            try:
                session_id = f"session_{uuid.uuid4().hex[:7]}"
                resp = await client.post(
                    f"{AI_AGENT_URL}/apps/remediator/users/remediator/sessions/{session_id}",
                    timeout=60,
                )
                resp.raise_for_status()
                session = resp.json()
            except httpx.HTTPError as e:
                raise HTTPException(
                    status_code=500, detail=f"AI agent call failed: {str(e)}"
                )

        connection, channel = await connect_rabbitmq()
        exchange = await channel.declare_exchange(
            exchange_name, aio_pika.ExchangeType.TOPIC, durable=True
        )

        queue = await channel.declare_queue("ai_agent_queue", durable=True)
        await queue.bind(exchange, routing_key=f"{authorized_namespace}.*.*")
        await queue.bind(exchange, routing_key=f"cluster.*.*")

        await sub(authorized_namespace, queue, session, channel)

    finally:
        if session:
            async with httpx.AsyncClient() as client:
                try:
                    resp = await client.delete(
                        f"{AI_AGENT_URL}/apps/remediator/users/remediator/sessions/{session['id']}",
                        timeout=60,
                    )
                    resp.raise_for_status()
                except httpx.HTTPError as e:
                    raise HTTPException(
                        status_code=500, detail=f"AI agent call failed: {str(e)}"
                    )
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
