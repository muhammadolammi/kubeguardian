import asyncio
import json
import os
import sys
import aio_pika
from session.session import create_new_session
from guardian.agent import get_remediator_agent
from google.adk import Agent
from guardian.run import run

EVENTS = ["ERROR", "DELETED", "WARNING", "ADDED"]

async def handle_message(agent: Agent, session_data: dict, body: bytes):
    """Handle incoming RabbitMQ messages."""
    message = json.loads(body.decode("utf-8"))
    event_type = message.get("type")
    deployment = message["name"],
    print(f"[x] Received event: {event_type} for {deployment}")
    # Call AI Remediator
    agent_response = await run(agent=agent, session_data=session_data, message=body.decode("utf-8"))
    print(f"[AI Response] {agent_response}")


async def deployment_sub(agent: Agent, namespace: str, session_data: dict):
    """Async subscriber that listens for deployment events."""
    connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq:5672/")
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
                    await handle_message(agent, session_data, message.body)


async def async_main():
    authorized_namespace = "bank-of-anthos"
    agent = get_remediator_agent(authorized_namespace)
    session_id = await create_new_session("remediator")

    await deployment_sub(
        agent,
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
