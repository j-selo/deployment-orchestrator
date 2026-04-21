import time
from schemas import DeployRequest

def validate_request(req):
    allowed_envs = ["dev", "stg", "prod"]

    if req.env not in allowed_envs:
        raise ValueError(f"Invalid environment: {req.env}")

    if req.service == "":
        raise ValueError("Service name required")