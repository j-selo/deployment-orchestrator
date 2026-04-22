import datetime
from pydantic import BaseModel

class DeployRequest(BaseModel):
    service: str
    image: str
    env: str
    time: datetime.datetime
class DeployResponse(BaseModel):
    id: str
    status: str