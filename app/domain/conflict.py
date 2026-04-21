import time
from schemas import DeployRequest

async def ensure_no_conflicts(repo, req: DeployRequest):
    active = await repo.find_active_by_env(req.env)
    if active:
        raise Exception(
            f"Conflict: deployment already running in {req.env}"
        )