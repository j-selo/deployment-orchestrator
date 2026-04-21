import uuid
from datetime import datetime

class DeployRepository:
    def __init__(self, db):
        self.db = db

    async def create(self, req):
        deploy_id = str(uuid.uuid4())
        await self.db.execute(
            """
            INSERT INTO deployments (id, service, env, image, status)
            VALUES ($1, $2, $3, $4, $5)
            """,
            deploy_id,
            req.service,
            req.env,
            req.image,
            "scheduled"
        )

        return deploy_id