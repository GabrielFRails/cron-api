from fastapi import FastAPI, HTTPException, Path
from typing import List, Dict
import uuid

from libapi import *
from libapidata import *

app = FastAPI()

@app.get("/jobs/user")
def get_user_cron_jobs(user: str):
# {
	result = api_crontab_get(user)
	if not result:
		error_msg = f"Erro ao ler o crontab do usuário '{user}'"
		raise HTTPException(status_code=500, detail=error_msg)
	return result
# }

@app.get("/jobs/{user}/{id}")
def get_cron_job(
	user: str = Path(description="Linux user name"),
	id: str = Path(description="cron job id")
):
# {
	result = api_cronjob_get_by_id(user, id)
	if not result:
		error_msg = f"Erro ao ler o crontab do usuário {user}: {result.stderr}"
		raise HTTPException(status_code=500, detail=error_msg)
	return result
# }

@app.post("/jobs/create/{user}")
async def create_cron_job(
    job: CronJob,
    user: str = Path(description="Linux user name")
):
# {
	cjid = str(uuid.uuid4()).split("-")[0]
	cron_line = f"\n#cjid:{cjid} % Created by cron-api\n{job.schedule} {job.command}\n"
	r = api_cronjob_add(user, cron_line)

	if not r:
		raise HTTPException(status_code=500, detail="Erro ao adicionar novo cron job")
	
	dict_job = job.__dict__
	dict_job['cid'] = cjid
	return {"message": "Created", "job": dict_job}
# }

@app.delete("/jobs/delete/{user}/{id}")
def delete_cron_job(
	user: str = Path(description="Linux user name"),
	id: str = Path(description="cron job id")
):
# {
	r = api_cronjob_delete(user, id)
	if not r:
		raise HTTPException(status_code=500, detail="Erro ao deletar cron job {id}")
	
	return Response(status_code=204)
# }

@app.put("/jobs/create/{user}")
def update_cron_job(
	job: CronJob,
	id: str = Path(description="cron job id to be updated"),
	user: str = Path(description="Linux user name")
):
# {
	updated_cron_job = f"{job.schedule} {job.command}"
	r = api_cronjob_update(user, id, updated_cron_job)

	if not r:
		raise HTTPException(status_code=500, detail="Erro ao editar cron job")

	job['cid'] = id
	return {"message": "Updated", "job": job.dict()}
# }