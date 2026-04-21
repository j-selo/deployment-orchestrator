import temporalio.worker
import temporalio.TemporalioClient
import asyncio

from workflows import SchedulerDeployWorkflow
from activites import (
    deploy_activity,
    health_check_activity,
    rollback_activity,
    notify_activity
)

async def main():
    # Connect to Temporal server
    client = await TemporalioClient.connect("localhost:7233")

    # Create a worker and register the workflow and activities
    worker = temporalio.worker.Worker(
        client,
        task_queue="deploy-queue",
        workflows=[SchedulerDeployWorkflow],
        activities=[
            deploy_activity,
            health_check_activity,
            rollback_activity,
            notify_activity
        ]
    )

    # Run the worker
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())