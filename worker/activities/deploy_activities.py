from temporalio import activity
from app.core.db import get_db
from app.integrations.helm import helm_deploy
from app.integrations.kubernetes import wait_for_rollout
from app.integrations.rollback import helm_rollback
from app.integrations.slack import notify_start, notify_end

DEFAULT_CHART_PATH = "../charts/myapp"
DEFAULT_NAMESPACE = "default"


@activity.defn
async def deploy_activity(deploy_id: str):
    db = await get_db()
    print(f"Deploying with ID: {deploy_id}")
    await helm_deploy(deploy_id, DEFAULT_CHART_PATH, DEFAULT_NAMESPACE)
    await db.execute(
        "UPDATE deployments SET status = $1 WHERE id = $2",
        "deploying",
        deploy_id
    )
    return f"Deployment {deploy_id} completed"

@activity.defn
async def health_check_activity(deploy_id: str):
    db = await get_db()
    print(f"Performing health check for deployment ID: {deploy_id}")

    rollout = await wait_for_rollout(
        namespace=DEFAULT_NAMESPACE,
        deployment_name=deploy_id,
    )

    if not rollout["healthy"]:
        await db.execute(
            "UPDATE deployments SET status = $1 WHERE id = $2",
            "failed",
            deploy_id,
        )
        issues = ", ".join(rollout["pod_issues"])
        raise RuntimeError(f"Health check failed for deployment {deploy_id}: {issues}")

    await db.execute(
        "UPDATE deployments SET status = $1 WHERE id = $2",
        "deployed",
        deploy_id,
    )

    return f"Health check for deployment {deploy_id} passed"    

@activity.defn
async def rollback_activity(deploy_id: str):
    db = await get_db()
    print(f"Rolling back deployment with ID: {deploy_id}")
    await db.execute(
        "UPDATE deployments SET status = $1 WHERE id = $2",
        "rolling_back",
        deploy_id,
    )
    await helm_rollback(deploy_id, DEFAULT_NAMESPACE)
    await db.execute(
        "UPDATE deployments SET status = $1 WHERE id = $2",
        "rolled_back",
        deploy_id,
    )
    return f"Rollback for deployment {deploy_id} completed"

# @activity.defn
# async def notify_activity(deploy_id: str, message: str):
#     db = await get_db()
#     await db.execute(
#         "UPDATE deployments SET status = $1 WHERE id = $2",
#         "notifying",
#         deploy_id,
#     )
#     await notify_start(deploy_id, message)
#     await notify_end(deploy_id, message)
#     await db.execute(
#         "UPDATE deployments SET status = $1 WHERE id = $2",
#         "notified",
#         deploy_id,
#     )
#     print(f"Notifying about deployment ID: {deploy_id} with message: {message}")
#     return f"Notification for deployment {deploy_id} sent with message: {message}"

