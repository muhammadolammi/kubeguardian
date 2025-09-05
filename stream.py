


from kubernetes import client, config, watch
import asyncio
from guardian.run import run
from google.adk.sessions import InMemorySessionService


from const import logger
from google.adk.agents import Agent



CRITICAL_POD_REASONS = ["CrashLoopBackOff", "Failed", "ImagePullBackOff"]
CRITICAL_DEPLOYMENT_REASONS = ["ProgressDeadlineExceeded", "FailedCreate", "ReplicaFailure"]


async def stream_pods(agent: Agent, namespace: str, session_service: InMemorySessionService, session_data: dict):
    """
    Stream Pod events in the given namespace.
    Calls orchestrator if any container has a critical reason.
    """
    config.load_kube_config()
    v1 = client.CoreV1Api()
    w = watch.Watch()

    for event in w.stream(v1.list_namespaced_pod, namespace=namespace):
        
        event_type = event.get("type")
        pod_obj: client.V1Pod = event.get("object")

        # Aggregate all waiting reasons from containers
        reasons = []
        if pod_obj and pod_obj.status and pod_obj.status.container_statuses:
            for cs in pod_obj.status.container_statuses:
                if cs.state and cs.state.waiting and cs.state.waiting.reason:
                    reasons.append(cs.state.waiting.reason)

        payload = {
            "type": event_type,
            "pod_name": pod_obj.metadata.name if pod_obj.metadata else "",
            "reasons": reasons,
        }

        # Trigger orchestrator if any reason is critical
        if event_type in ["ERROR", "DELETED", "WARNING"]  or any(r in CRITICAL_POD_REASONS for r in reasons):
            logger.info("Email ageny called...")
            ai_response = await run(
                agent=agent,
                session_service=session_service,
                session_data=session_data,
                message=f"{payload}",
                output_key="orchestrator_response"
            )
            logger.info(f"Pod issue handled for {pod_obj.metadata.name}: {ai_response}")
            print(ai_response)
        else:
            logger.debug(f"Ignored pod event {pod_obj.metadata.name}, reasons: {reasons or '(none)'}")

        await asyncio.sleep(0)


async def stream_deployments(agent:Agent,namespace: str, session_service: InMemorySessionService, session_data: dict):
    """
    Stream Deployment events in the given namespace.
    Calls orchestrator if any critical deployment condition is found.
    """
    config.load_kube_config()
    apps_v1 = client.AppsV1Api()
    w = watch.Watch()

    for event in w.stream(apps_v1.list_namespaced_deployment, namespace=namespace):
        event_type = event.get("type")
        deploy_obj: client.V1Deployment = event.get("object")

        # Aggregate all relevant reasons
        reasons = []
        if deploy_obj and deploy_obj.status and deploy_obj.status.conditions:
            for cond in deploy_obj.status.conditions:
                if cond.reason:
                    reasons.append(cond.reason)
                # Prioritize rollout failures
                if cond.type == "Progressing" and cond.reason == "ProgressDeadlineExceeded":
                    reasons.append(cond.reason)

        payload = {
            "type": event_type,
            "deployment_name": deploy_obj.metadata.name if deploy_obj.metadata else "",
            "reasons": reasons,
            
        }

        # Trigger orchestrator if any critical reason exists
        if event_type in ["ERROR", "DELETED", "WARNING"]  or any(r in CRITICAL_DEPLOYMENT_REASONS for r in reasons):
            ai_response = await run(
                agent=agent,
                session_service=session_service,
                session_data=session_data,
                message=f"{payload}",
                output_key="orchestrator_response"
            )
            logger.info(f"Deployment issue handled for {deploy_obj.metadata.name}: {ai_response}")
            print(ai_response)
        else:
            logger.debug(f"Ignored deployment event {deploy_obj.metadata.name}, reasons: {reasons or '(none)'}")

        await asyncio.sleep(0)