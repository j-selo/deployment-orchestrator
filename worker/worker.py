import temporalio.worker
from temporalio.client import Client
import asyncio

from worker.workflows.deploy_workflows import DeployWorkflow
from worker.activities.deploy_activities import (
    deploy_activity,
    health_check_activity,
    rollback_activity,
    # notify_activity
)

async def main():
    # Connect to Temporal server
    client = await Client.connect("localhost:7233")

    # Create a worker and register the workflow and activities
    worker = temporalio.worker.Worker(
        client,
        task_queue="deploy-queue",
        workflows=[DeployWorkflow],
        activities=[
            deploy_activity,
            health_check_activity,
            rollback_activity,
            # notify_activity
        ]
    )

    # Run the worker
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())