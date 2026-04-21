from datetime import datetime, timedelta

# Ensure only one prod deploy at a time
async def ensure_single_prod_deploy(repo, req):
    if req.env == "prod":
        active = await repo.find_active_by_env("prod")
        if active:
            raise Exception("Another production deployment is already running")


# Deployments to prod during business hours
def block_business_hours(req):
    now = datetime.now().astimezone().hour
    if req.env == "prod" and not 9 <= now <= 17:
        raise Exception("Prod deploys are only allowed during business hours")


# Prod deployments require approval
def require_prod_approval(req):
    if req.env == "prod" and not req.approved:
        raise Exception("Production deployments require approval")


# Block if error rate is high
async def check_error_rate(repo, req):
    error_rate = await repo.get_error_rate(req.service)
    if error_rate > 0.05:  # 5%
        raise Exception("Service error rate too high for deployment")


# Limit deploy frequency (e.g., 1 every 10 minutes)
async def enforce_deploy_frequency(repo, req):
    last = await repo.get_last_deploy(req.service)
    if last:
        delta = datetime.now().astimezone() - last.created_at
        if delta < timedelta(minutes=10):
            raise Exception("Deploy too soon after last deployment")