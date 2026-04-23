from domain import policies
from domain.validators import validate_request
from domain.conflict import ensure_no_conflicts

class DeployService:
    def __init__(self, repo, orchestrator):
        self.repo = repo
        self.orchestrator = orchestrator

    async def schedule(self, req):
         # Validate Rules (domain/validators.py)
        validate_request(req)
        
        # Check Conflicts (domain/conflict.py)
        await ensure_no_conflicts(self.repo, req)
        
        # Check Policies (domain/policies.py)
        policies.block_business_hours(req)
        
        # Policy checks that require repo access (domain/policies.py)
        await policies.ensure_single_prod_deploy(self.repo, req)
        await policies.enforce_deploy_frequency(self.repo, req)
        await policies.check_error_rate(self.repo, req)

        # If all checks pass, create deploy record and start workflow
        deploy_id = await self.repo.create(req)
        await self.orchestrator.start_workflow(deploy_id, req)
        return deploy_id
    



