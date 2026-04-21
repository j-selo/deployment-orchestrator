from fastapi import APIRouter

router = APIRouter()

# Creating a POST API endpoint for handling deployment requests
@router.post("/")
def deploy():
    return {"message": "Deployment request received"}