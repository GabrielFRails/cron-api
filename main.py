from fastapi import FastAPI, HTTPException
from subprocess import run, PIPE, Popen
from typing import List, Dict
import os
import uuid

from libapi import *
from libapidata import *

app = FastAPI()

@app.get("/jobs/user")
def get_user_cron_jobs(user: str):
    success, result = api_crontab_get(user)
    if not success:
        raise HTTPException(status_code=500, detail=str(result))
    return result

@app.get("/jobs/user/id")
def get_cron_job(user: str, id: str):
    success, result = api_cronjob_get_by_id(user, id)
    if not success:
        raise HTTPException(status_code=500, detail=str(result))
    return result

@app.post("/jobs/create-cron")
async def create_cron_job(job: CronJob):
    cjid = str(uuid.uuid4()).split("-")[0]
    cron_line = f"\n#cjid:{cjid} % Created by cron-api\n{job.schedule} {job.command}\n"
    success, message = add_cron_job(cron_line)

    if not success:
        raise HTTPException(status_code=500, detail=message)
    
    return {"message": message, "job": job.dict()}