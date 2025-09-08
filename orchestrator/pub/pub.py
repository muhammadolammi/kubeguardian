

import asyncio
import logging
import sys
from kubernetes import client, config, watch
import aio_pika
from ..helpers import process_event, connect_rabbitmq,stream_k8s_events, serialize_event_obj, classify_event
from kubernetes.client import ApiClient
#Mainly for seriliazation
api_client = ApiClient()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

DEPLOYMENT_EVENTS = ["ERROR", "DELETED", "WARNING"]
POD_EVENTS = ["ERROR", "DELETED", "WARNING"]






async def deployment_pub(namespace: str):
    """Watch Kubernetes deployments and publish events forever."""
    RESOURCE_NAME="Deployment"

    # Load kube config
    try:
        config.load_kube_config() 
    except config.ConfigException:
        config.load_incluster_config()

    apps_v1 = client.AppsV1Api()
    w = watch.Watch()

    while True:
        try:
            connection = await connect_rabbitmq()
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=1)

            exchange_name = f"{namespace}_{RESOURCE_NAME}"
            await channel.declare_exchange(
                exchange_name, aio_pika.ExchangeType.DIRECT, durable=True
            )

            logger.info("Starting Kubernetes watch...")
            async for event in stream_k8s_events(apps_v1.list_namespaced_deployment, namespace, w):
                payload = serialize_event_obj(event, RESOURCE_NAME)
                await process_event(channel, payload, exchange_name, RESOURCE_NAME, DEPLOYMENT_EVENTS)
                
        
        except Exception as e:
            logger.error(f"Failed to publish a deployment event. error: {e}, retrying in 5 seconds...")
            await asyncio.sleep(5)




async def pod_pub(namespace: str):
    """Watch Kubernetes pods and publish events forever."""
    RESOURCE_NAME="Pod"
    # Load kube config
    try:
        config.load_kube_config() 
    except config.ConfigException:
        config.load_incluster_config()

    core_v1 = client.CoreV1Api()
    w = watch.Watch()

    while True:
        try:
            connection = await connect_rabbitmq()
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=1)

            exchange_name = f"{namespace}_{RESOURCE_NAME}"
            await channel.declare_exchange(
                exchange_name, aio_pika.ExchangeType.DIRECT, durable=True
            )

            logger.info("Starting Kubernetes watch...")
            async for event in stream_k8s_events(core_v1.list_namespaced_pod, namespace, w):
                payload = serialize_event_obj(event, RESOURCE_NAME)
                await process_event(channel, payload, exchange_name, RESOURCE_NAME, POD_EVENTS)
                
        
        except Exception as e:
            logger.error(f"Failed to publish a pod event. error: {e}, retrying in 5 seconds...")
            await asyncio.sleep(5)




async def main():
    authorized_namespace = "default"
    await asyncio.gather(
        deployment_pub(authorized_namespace),
        pod_pub(authorized_namespace),
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted")
        sys.exit(0)
