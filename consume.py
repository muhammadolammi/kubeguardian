import json
import pika
import aiohttp
import asyncio

RABBITMQ_HOST = "rabbitmq"
QUEUE_NAME = "deployment_events"
AI_URL = "http://ai-service:8000/infer"  # Your AI service endpoint

async def call_ai_model(payload):
    async with aiohttp.ClientSession() as session:
        async with session.post(AI_URL, json=payload) as resp:
            result = await resp.json()
            print(f"AI result: {result}")
            return result

async def handle_message(payload, ch, method):
    try:
        await call_ai_model(payload)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"AI call failed: {e}")
        # Nack without requeue if you don’t want infinite retries
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def consume_events():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)

    loop = asyncio.get_event_loop()

    def callback(ch, method, properties, body):
        payload = json.loads(body.decode("utf-8"))
        asyncio.run_coroutine_threadsafe(
            handle_message(payload, ch, method), loop
        )

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    print(" [*] Waiting for deployment events...")
    loop.run_in_executor(None, channel.start_consuming)
    loop.run_forever()

if __name__ == "__main__":
    consume_events()
