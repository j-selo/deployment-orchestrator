from fastapi import FastAPI
from api.routes import deploy

app = FastAPI()

app.include_router(deploy.router, prefix="/deploy")