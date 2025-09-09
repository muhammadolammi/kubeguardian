
import asyncio
import logging
import sys
from kubernetes import client, config, watch
import aio_pika
from ..helpers import process_event, connect_rabbitmq,stream_k8s_events, serialize_event_obj, classify_event
shutdown_event = asyncio.Event()

# shutdown_event = asyncio.Event()

from ..const import exchange_name

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)
#Load configs before defining apis
 # Load kube config
try:
    logger.info("Loaded local config")

    config.load_kube_config() 
except config.ConfigException:
    logger.info("Loaded in-cluster kubeconfig")
    config.load_incluster_config()
RESOURCE_API_MAP = {
    "Deployment": client.AppsV1Api().list_namespaced_deployment,
    "Pod": client.CoreV1Api().list_namespaced_pod,
    "ReplicaSet": client.AppsV1Api().list_namespaced_replica_set,
    "Node": client.CoreV1Api().list_node,
    "Service": client.CoreV1Api().list_namespaced_service,
    "Ingress": client.NetworkingV1Api().list_namespaced_ingress,
    "ConfigMap": client.CoreV1Api().list_namespaced_config_map,
    "Secret": client.CoreV1Api().list_namespaced_secret,
    "PersistentVolume": client.CoreV1Api().list_persistent_volume,
    "PersistentVolumeClaim": client.CoreV1Api().list_namespaced_persistent_volume_claim,
    }   

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



async def pub(namespace: str, RESOURCE_NAME:str, channel):
    """Watch Kubernetes RESOURCE and publish events forever.""" 
    api_function = RESOURCE_API_MAP[RESOURCE_NAME]
    EVENTS_TO_STREAM= RESOURCE_EVENTS_MAP[RESOURCE_NAME]
    if not api_function:
        logger.info("Invalid resource name provided")
        return
    w = watch.Watch()
    

    while True:
        try:
            logger.info("Starting Kubernetes watch...")
            if RESOURCE_NAME in ["Node", "PersistentVolume"]:
                # Stream cluster wide resorces
                async for event in stream_k8s_events(api_function=api_function, namespace=None, w=w):
                    payload = serialize_event_obj(event, RESOURCE_NAME)
                    await process_event(channel, payload, exchange_name, RESOURCE_NAME, EVENTS_TO_STREAM)
            else:    
                async for event in stream_k8s_events(api_function=api_function, namespace=namespace, w=w):
                    payload = serialize_event_obj(event, RESOURCE_NAME)
                    await process_event(channel, payload, exchange_name, RESOURCE_NAME, EVENTS_TO_STREAM)
        
        except Exception as e:
            logger.error(f"Failed to publish a {RESOURCE_NAME} event. error: {e}, retrying in 5 seconds...")
            await asyncio.sleep(5)
        







async def main():
    authorized_namespace = "default"
    connection, channel = await connect_rabbitmq()
    try:
        await channel.set_qos(prefetch_count=1)
        await channel.declare_exchange(
            exchange_name, aio_pika.ExchangeType.TOPIC, durable=True
        )
        await asyncio.gather(
            pub(authorized_namespace, "Deployment", channel),
            pub(authorized_namespace, "Pod", channel),
            pub(authorized_namespace, "ReplicaSet", channel),
            pub(authorized_namespace, "Node", channel),
            pub(authorized_namespace, "Service", channel),
            pub(authorized_namespace, "Ingress", channel),
            pub(authorized_namespace, "ConfigMap", channel),
            pub(authorized_namespace, "PersistentVolume", channel),
            pub(authorized_namespace, "PersistentVolumeClaim", channel),
        )
    finally:
        await channel.close()
        await connection.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted")
        sys.exit(0)
