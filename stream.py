


from kubernetes import client, config, watch
import asyncio
from guardian.run import run

from const import logger, agent
#Create global agent

def getconfig()-> dict:
    return {} 


async def stream_pods():
    config.load_kube_config()
    v1 = client.CoreV1Api()
    w = watch.Watch()
    payload_config = getconfig()
    payload = {}
    payload["config"]= payload_config
    # loop = asyncio.get_event_loop()
    # TODO send config to ai base on namespace, to define authorization
    #TODO we need to somehow define what the ai needs to automatically solved based on criticality and access.
    #TODO Also where to send alert.
    #TODO also includes every action taken by the ai in our web ui
    for event in w.stream(v1.list_pod_for_all_namespaces):
        
        
        # Lets call the ai directly here 
        payload["event"] = event
        # ai_response = asyncio.run(run(agent=agent, payload=f"{payload}"))
        ai_response = await run(agent=agent, payload=f"{payload}")

        logger.info("Autonomous System Started")
        print(ai_response)

        # TODO handlee ai response here

        await asyncio.sleep(0)
        
        
#TODO  COPY STREAM FUNCTION for diffrent scanario other than "v1.list_pod_for_all_namespaces" i.e get deployment in namespaces


