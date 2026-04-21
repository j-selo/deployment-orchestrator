# app/state/status.py
from app.core.db import get_db


async def update_deploy_status(deploy_id: str, status: str) -> None:
    conn = await get_db()
    try:
        await conn.execute(
            "UPDATE deployments SET status = $1 WHERE id = $2",
            (status, deploy_id),
        )
        await conn.commit()
    finally:
        await conn.close()

    print(f"Deployment status updated for ID: {deploy_id} to status: {status}")