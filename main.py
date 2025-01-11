from fastapi import FastAPI, HTTPException, Path
from typing import List, Dict
import uuid

from libapi import *
from libapidata import *

app = FastAPI()

@app.get("/jobs/user")
def get_user_cron_jobs(user: str):
	result = api_crontab_get(user)
	if not result:
		error_msg = f"Erro ao ler o crontab do usuário {user}: {result.stderr}"
		raise HTTPException(status_code=500, detail=error_msg)
	return result

@app.get("/jobs/{user}/{id}")
def get_cron_job(
	user: str = Path(description="Linux user name"),
	id: str = Path(description="cron job id")
):
	result = api_cronjob_get_by_id(user, id)
	if not result:
		error_msg = f"Erro ao ler o crontab do usuário {user}: {result.stderr}"
		raise HTTPException(status_code=500, detail=error_msg)
	return result

@app.post("/jobs/create-cron")
async def create_cron_job(job: CronJob):
	cjid = str(uuid.uuid4()).split("-")[0]
	cron_line = f"\n#cjid:{cjid} % Created by cron-api\n{job.schedule} {job.command}\n"
	success, message = add_cron_job(cron_line)

	if not success:
		raise HTTPException(status_code=500, detail=message)
	
	return {"message": message, "job": job.dict()}