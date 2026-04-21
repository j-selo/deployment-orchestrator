import slack
import os
import time, datetime
from app.schemas.schema import DeployRequest

class SlackNotifier:
    def __init__(self):
        self.client = slack.WebClient(token=os.environ["SLACK_BOT_TOKEN"])
        self.channel = os.environ["SLACK_CHANNEL"]

    async def notify_deploy_start(self, req: DeployRequest):
        await self.client.chat_postMessage(
            channel=self.channel,
            text=f"Deployment started for {req.service} in {req.env} at {req.time}"
        )

    async def notify_deploy_end(self, req: DeployRequest, success=True):
        status = "succeeded" if success else "failed"
        await self.client.chat_postMessage(
            channel=self.channel,
            text=f"Deployment {status} for {req.service} in {req.env} at {datetime.datetime.now()}"
        )