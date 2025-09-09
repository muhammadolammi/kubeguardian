from const import get_ENV
rabbitmq_url = get_ENV("RABBITMQ_URL")
AI_AGENT_URL = get_ENV("AI_AGENT_URL")

import asyncio
import json
import os
import sys
import aio_pika
from session.session import create_new_session
import httpx


EVENTS = ["ERROR", "DELETED", "WARNING", "ADDED"]

async def handle_message(namespace:str, session_data: Payload, body: bytes):
    """Handle incoming RabbitMQ messages."""
    message = json.loads(body.decode("utf-8"))
    event_type = message.get("type")
    deployment = message["name"],
    print(f"[x] Received event: {event_type} for {deployment}")
    # Prepare payload for AI agent
    payload = {
        "agent_type": "remediator",
        "namespace": namespace,
        "user_id": session_data.get("user_id"),
        "session_id": session_data.get("session_id"),
        "message": json.dumps(message)  # send full message as text
    }

    # Send to AI agent service
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(AI_AGENT_URL, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            agent_response = data.get("response")
            print(f"[AI Response] {agent_response}")
            return agent_response
        except httpx.HTTPError as e:
            print(f"[!] Failed to call AI agent: {e}")
            return f"⚠️ AI agent call failed: {str(e)}"
    

async def deployment_sub( namespace: str, session_data: dict):
    """Async subscriber that listens for deployment events."""
    connection = await aio_pika.connect_robust(rabbitmq_url)
    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)

        exchange_name = f"{namespace}_deployments"
        exchange = await channel.declare_exchange(exchange_name, aio_pika.ExchangeType.DIRECT, durable=True)

        queue_name = f"{namespace}_deployment_queue"
        queue = await channel.declare_queue(queue_name, durable=True)

        # Bind queue to all event routing keys
        for event in EVENTS:
            await queue.bind(exchange, routing_key=event)

        print("[*] Waiting for messages. To exit press CTRL+C")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process(ignore_processed=True):
                    await handle_message(namespace, session_data, message.body)


async def async_main():
    authorized_namespace = "bank-of-anthos"
    session_id = await create_new_session("remediator")

    await deployment_sub(
        authorized_namespace,
        {"user_id": "remediator", "session_id": session_id},
    )

if __name__ == '__main__':
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
