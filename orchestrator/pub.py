import pika 
from kubernetes import client, config, watch
import sys
import os
import logging
import json
import time
# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr,  # ✅ Logs to stderr
)
logger = logging.getLogger(__name__)


CRITICAL_POD_REASONS = ["CrashLoopBackOff", "Failed", "ImagePullBackOff"]
CRITICAL_DEPLOYMENT_REASONS = ["ProgressDeadlineExceeded", "FailedCreate", "ReplicaFailure"]
EVENTS=["ERROR", "DELETED", "WARNING", "ADDED"] 


def process_event(channel, event, exchange_name):
    event_type = event.get("type")
    deploy_obj: client.V1Deployment = event.get("object")
    important_reason = None
    if deploy_obj and deploy_obj.status and deploy_obj.status.conditions:
        for cond in deploy_obj.status.conditions:
            if cond.type == "Progressing" and cond.reason == "ProgressDeadlineExceeded":
                important_reason = cond.reason
                break
            elif cond.reason in CRITICAL_DEPLOYMENT_REASONS:
                important_reason = cond.reason
            elif not important_reason:
                important_reason = cond.reason

    payload = {
        "type": event_type,
        "deployment_name": deploy_obj.metadata.name if deploy_obj.metadata else "",
        "reason": important_reason,
    }
    should_capture = event_type in EVENTS or important_reason in CRITICAL_DEPLOYMENT_REASONS

    if should_capture:
        routing_key = event_type
        channel.basic_publish(
            exchange=exchange_name,
            routing_key=routing_key,
            body=json.dumps(payload),
            properties=pika.BasicProperties(delivery_mode=2)  # Persistent messages
        )
        logger.info(f"Published: {payload}")


def deployment_pub(namespace:str):
    """
    Publish Deployment events in the given namespace.
    """
    # RabbitMQ connection
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

    channel = connection.channel()
    # Declare Exchange
    exchange_name = f"{namespace}_deployments"
    channel.exchange_declare(exchange=exchange_name, exchange_type='direct', durable=True)
    # Only send one acknoldged message to subs/consumers
    channel.basic_qos(prefetch_count=1)


    try:
        config.load_kube_config()
        # After deplopyed in a pod run 
        #config.load_incluster_config()
        # logger.info("Loaded kubeconfig for Minikube")
    except Exception as e:
        logger.error(f"Failed to load kubeconfig: {e}")
        sys.exit(1)
    apps_v1 = client.AppsV1Api()
    w = watch.Watch()
    # cfg = client.Configuration.get_default_copy()
    # print(f"Kubernetes API endpoint: {cfg.host}")
    while True:
        try:
            for event in w.stream(apps_v1.list_namespaced_deployment, namespace=namespace):
                process_event(channel, event, exchange_name)
        except Exception as e:
            print(f"Watch failed: {e}, retrying again in 5 seconds... ")
            time.sleep(5)


def main():
    # WE can alwasy move this logic , maybe get it from env
    authorized_namespace = "bank-of-anthos"
    deployment_pub(authorized_namespace)
    # threading.Thread(target=deployment_pub, args=("main",), daemon=True).start()
    
    # # Start pod watcher in another thread
    # threading.Thread(target=pod_pub, args=("main",), daemon=True).start()
    
    # # Keep main alive
    # while True:
    #     pass


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)