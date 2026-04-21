from temporalio import activity
from app.core.db import get_db
from integrations import helm_deploy


@activity.defn
async def deploy_activity(deploy_id: str):
    db = await get_db()
    print(f"Deploying with ID: {deploy_id}")
    await helm_deploy(deploy_id, "chart_path", "namespace")
    await db.execute(
        "UPDATE deployments SET status = $1 WHERE id = $2",
        "deployed",
        deploy_id
    )
    return f"Deployment {deploy_id} completed"

async def health_check_activity(deploy_id: str):

    print(f"Performing health check for deployment ID: {deploy_id}")
    return f"Health check for deployment {deploy_id} passed"    

@activity.defn
async def rollback_activity(deploy_id: str):
   
    print(f"Rolling back deployment with ID: {deploy_id}")
    return f"Rollback for deployment {deploy_id} completed"

@activity.defn
async def notify_activity(deploy_id: str, message: str):
  
    print(f"Notifying about deployment ID: {deploy_id} with message: {message}")
    return f"Notification for deployment {deploy_id} sent with message: {message}"

