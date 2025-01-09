from fastapi import FastAPI, HTTPException
from subprocess import run, PIPE, Popen
from typing import List, Dict
import os

from libapi import *
from libapidata import *

app = FastAPI()

@app.get("/jobs/user")
def get_user_cron_jobs(user: str):
    success, result = api_crontab_get(user)
    if not success:
        raise HTTPException(status_code=500, detail=str(result))
    return result

CRON_JOBS_DIR = "./"

@app.post("/jobs/create-cron")
async def create_cron_job(job: CronJob):
	cron_line = f"\n#Created by cron-api\n{job.schedule} {job.command}\n"
	current_crontab = run(["crontab", "-l"], stdout=PIPE, stderr=PIPE, text=True)
	
	if current_crontab.returncode == 0:
		new_crontab = current_crontab.stdout + cron_line
	else:
		new_crontab = cron_line  # Caso não haja crontab atual

	p = Popen(['crontab', '-'], stdin=PIPE, stdout=PIPE, stderr=PIPE, text=True)
	stdout, stderr = p.communicate(input=new_crontab)

	if p.returncode != 0:
		raise HTTPException(status_code=500, detail=f"Erro ao atualizar crontab: {stderr}")
	
	return {"message": "Cron job adicionado com sucesso", "job": job.dict()}