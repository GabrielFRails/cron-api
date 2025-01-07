from fastapi import FastAPI, HTTPException
from subprocess import run, PIPE
from typing import List, Dict

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

	for line in crontab_content.split("/n"):
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