from temporalio.client import Client
from worker.workflows.deploy_workflows import DeployWorkflow

async def get_temporal_client():
    client = await Client.connect("localhost:7233")
    return client

async def start_workflow(deploy_id: str) -> str:
    client = await get_temporal_client()
    handle = await client.start_workflow(
        DeployWorkflow.run,
        deploy_id,
        id=f"deploy-{deploy_id}",
        task_queue="deploy-queue"
    )
    return handle.id