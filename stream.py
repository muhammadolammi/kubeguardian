


from kubernetes import client, config, watch
import asyncio
from guardian.run import run
from google.adk.sessions import InMemorySessionService


from const import logger,  orchestrator_agent
LAST_CALL = 0
MIN_INTERVAL = 6  # ~10 per minute
def getconfig()-> dict:
    return {} 


async def stream_pods(namespace:str, session_servie:InMemorySessionService, session_data:dict):
    """
    Stream pods in give namespace
    Args:
        namespace:str 
    """
    config.load_kube_config()
    v1 = client.CoreV1Api()
    w = watch.Watch()
    payload_config = getconfig()    
    # for event in w.stream(v1.list_pod_for_all_namespaces):
    for event in w.stream(v1.list_namespaced_pod, namespace=namespace):
        # Lets call the ai directly here 
        event_type = event.get("type")
        pod_obj = event.get("object", {})
        reason = pod_obj.get("reason", "")
        # status = pod_obj.get("status", {})
        payload = {"type": "pod", "namespace": namespace, "event": event, "config":payload_config}
        # Only call AI for specified pod reason
        if event_type == "ERROR" or reason in ["CrashLoopBackOff", "Failed", "ImagePullBackOff"]:

            ai_response = await run(agent=orchestrator_agent,session_service=session_servie, session_data=session_data, message=f"{payload}", output_key="orchestrator_response")

            logger.info("Autonomous System Started")
            print(ai_response)
        else: 
            print(f"Ignored event: {reason}")

        # TODO handlee ai response here

        await asyncio.sleep(0)
        
   # Stream Deployments
async def stream_deployments(namespace:str, session_servie:InMemorySessionService, session_data:dict):
    """
    Streams deployment in give namespace
    Args:
        namespace:str 
    """
    config.load_kube_config()
    apps_v1 = client.AppsV1Api()
    w = watch.Watch()
    payload_config = getconfig()
    
    for event in w.stream(apps_v1.list_namespaced_deployment, namespace=namespace):
        payload = {"type": "deployment", "namespace": namespace, "event": event, "config":payload_config}
        ai_response = await run(agent=orchestrator_agent,session_service=session_servie, session_data=session_data, message=f"{payload}", output_key="orchestrator_response")
        logger.info(f"Deployment event handled: {ai_response}")
        await asyncio.sleep(0)

