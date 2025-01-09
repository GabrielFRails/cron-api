from pydantic import BaseModel

class CronJob(BaseModel):
	schedule: str
	command: str