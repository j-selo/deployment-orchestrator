from temporalio import workflow
from datetime import timedelta
from worker.activities import (
    deploy_activity,
    health_check_activity,
    rollback_activity,
    notify_activity
)

@workflow.defn(name="DeployWorkflow")
class DeployWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        await workflow.execute_activity(
            deploy_activity,
            name,
            start_to_close_timeout=timedelta(minutes=10)
        )
        try:
            await workflow.execute_activity(
                health_check_activity,
                name,
                start_to_close_timeout=timedelta(minutes=5)
            )
        except Exception:
            await workflow.execute_activity(
                rollback_activity,
                name,
                start_to_close_timeout=timedelta(minutes=10)
            )
            return f"Deployment {name} failed, rollback completed"

        await workflow.execute_activity(
            notify_activity,
            args=[name, "Deployment completed successfully"],
            start_to_close_timeout=timedelta(minutes=2)
        )
        return f"Deployment {name} completed successfully"