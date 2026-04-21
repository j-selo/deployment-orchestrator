from temporalio import TemporalioClient
from app.core.db import get_db

async def get_temporal_client():
    # Connect to Temporal server
    client = await TemporalioClient.connect("localhost:7233")
    return client

async def run_workflow():
    client = await get_temporal_client()
    
    # Start the workflow
    handle = await client.start_workflow(
        "deploy_workflow",
        id="deploy_workflow_id",
        task_queue="deploy_task_queue"
    )
    print(f"Started workflow with ID: {handle.id}")
    await handle.result()
    print(f"Workflow completed {handle.result()}")