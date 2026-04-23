from fastapi import APIRouter
from db import get_db
from app.repositories.deploy_repo import DeployRepository
from app.services.deploy_service import DeployService
from temporalio.client import Client
from app.schemas import DeployRequest

router = APIRouter()

# Creating a POST API endpoint for handling deployment requests
@router.post("/")
async def deploy(req: DeployRequest):
    db        = await get_db()                      # Connect to the database
    repo      = DeployRepository(db)                # Load repository with DB connection
    client    = await Client.connect("localhost:7233")  # Connect to Temporal client
    service   = DeployService(repo, client)         # Load service with repository and Temporal client
    deploy_id = await service.schedule(req)         # Schedule deployment, trigger the workflow and status updates
    return {"message": f"Deployment request received {{'deploy_id': {deploy_id}}}"}