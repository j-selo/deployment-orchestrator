import asyncio
import os
from typing import Any

from kubernetes_asyncio import client, config


async def load_kube_config() -> None:
    if os.getenv("KUBERNETES_SERVICE_HOST"):
        config.load_incluster_config()
        return

    await config.load_kube_config()


def _container_waiting_reason(pod: client.V1Pod) -> str | None:
    for status in pod.status.container_statuses or []:
        waiting_state = status.state.waiting if status.state else None
        if waiting_state and waiting_state.reason:
            return waiting_state.reason
    return None


async def get_deployment_status(namespace: str, deployment_name: str) -> dict[str, Any]:
    await load_kube_config()
    api = client.AppsV1Api()
    deployment = await api.read_namespaced_deployment(
        name=deployment_name,
        namespace=namespace,
    )

    return {
        "name": deployment.metadata.name,
        "namespace": deployment.metadata.namespace,
        "generation": deployment.metadata.generation or 0,
        "observed_generation": deployment.status.observed_generation or 0,
        "desired_replicas": deployment.spec.replicas or 0,
        "updated_replicas": deployment.status.updated_replicas or 0,
        "available_replicas": deployment.status.available_replicas or 0,
        "ready_replicas": deployment.status.ready_replicas or 0,
        "selector": deployment.spec.selector.match_labels or {},
    }


async def list_pod_health_issues(namespace: str, label_selector: str) -> list[str]:
    await load_kube_config()
    api = client.CoreV1Api()
    pods = await api.list_namespaced_pod(namespace=namespace, label_selector=label_selector)

    issues: list[str] = []
    for pod in pods.items:
        waiting_reason = _container_waiting_reason(pod)
        if waiting_reason in {
            "CrashLoopBackOff",
            "ImagePullBackOff",
            "ErrImagePull",
            "CreateContainerConfigError",
        }:
            issues.append(f"{pod.metadata.name}: {waiting_reason}")
            continue

        if pod.status.phase not in {"Running", "Succeeded"}:
            issues.append(f"{pod.metadata.name}: phase={pod.status.phase}")
            continue

        for status in pod.status.container_statuses or []:
            if not status.ready:
                issues.append(f"{pod.metadata.name}: container {status.name} is not ready")

    return issues


async def wait_for_rollout(
    namespace: str,
    deployment_name: str,
    timeout_seconds: int = 180,
    poll_interval_seconds: int = 5,
) -> dict[str, Any]:
    attempts = max(timeout_seconds // poll_interval_seconds, 1)

    for _ in range(attempts):
        status = await get_deployment_status(namespace, deployment_name)
        selector = ",".join(
            f"{key}={value}" for key, value in status["selector"].items()
        )
        pod_issues = await list_pod_health_issues(namespace, selector) if selector else []

        rollout_complete = (
            status["observed_generation"] >= status["generation"]
            and status["updated_replicas"] == status["desired_replicas"]
            and status["available_replicas"] == status["desired_replicas"]
            and status["ready_replicas"] == status["desired_replicas"]
        )

        if rollout_complete and not pod_issues:
            return {
                "healthy": True,
                "deployment": status,
                "pod_issues": [],
            }

        if pod_issues:
            return {
                "healthy": False,
                "deployment": status,
                "pod_issues": pod_issues,
            }

        await asyncio.sleep(poll_interval_seconds)

    final_status = await get_deployment_status(namespace, deployment_name)
    return {
        "healthy": False,
        "deployment": final_status,
        "pod_issues": [
            "Timed out waiting for deployment rollout to become healthy"
        ],
    }