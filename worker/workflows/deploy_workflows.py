from temporalio import workflow, activities
from datetime import timedelta

@workflow.defn(name="DeployWorkflow")
class DeployWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        #1 - Deploy
        #2 - Wait for rollout
        #3 - Health check
        #4 - If health check passes, deploy is successful
        #5 - If health check fails, rollback