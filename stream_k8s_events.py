


from kubernetes import client, config, watch
import asyncio



def stream_k8s_events(callback):
    config.load_kube_config()
    v1 = client.CoreV1Api()
    w = watch.Watch()
    # loop = asyncio.get_event_loop()
    # TODO send config to ai base on namespace, to define authorization
    #TODO we need to somehow define what the ai needs to automatically solved based on criticality and access.
    #TODO Also where to send alert.
    #TODO also includes every action taken by the ai in our web ui
    for event in w.stream(v1.list_pod_for_all_namespaces):
        # print("event capcured: ")
        callback(event)
        
        




async def stream_k8s_events_async():
    # Load Kubernetes config
    config.load_kube_config()
    v1 = client.CoreV1Api()
    w = watch.Watch()

    logger.info("Starting to stream Kubernetes events...")

    # Stream events continuously
    try:
        for event in w.stream(v1.list_pod_for_all_namespaces):
            # Schedule the async callback without blocking the stream
            asyncio.create_task(handle_event(event))
    except Exception as e:
        logger.error(f"Error while streaming events: {e}")