from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from subprocess import run, PIPE, Popen
from typing import List, Dict
import os

app = FastAPI()

def run_crontab_command(user: str) -> str:
	try:
		result = run(['crontab', '-l', '-u', user], stdout=PIPE, stderr=PIPE, text=True, check=True)
		return result.stdout
	except:
		raise HTTPException(status_code=500, detail="Erro ao acessar o crontab do usuário")

@app.get("/jobs/user")
def get_user_jobs(user: str) -> List[Dict[str, str]]:
	jobs = []
	crontab_content = run_crontab_command(user)

	for line in crontab_content.split("\n"):
		line = line.strip()
		if line and not line.startswith("#"):
			parts = line.split(maxsplit=5)
			if len(parts) >= 6:
				schedule, command = ' '.join(parts[:5]), parts[5]
				jobs.append({
					"schedule": schedule,
					"command": command
				})
	
	return jobs

class CronJob(BaseModel):
	schedule: str
	command: str

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