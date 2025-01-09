from subprocess import run, PIPE

def run_crontab_command(user: str) -> str:
	try:
		result = run(['crontab', '-l', '-u', user], stdout=PIPE, stderr=PIPE, text=True, check=True)
		return True, result.stdout
	except:
		return False, f"Erro ao ler o crontab do usuário {user}: {result.stderr}"

def api_crontab_get(user: str) -> tuple[bool, list[dict] | str]:
	success, crontab_content = run_crontab_command(user)
	if not success:
		return False, crontab_content  # crontab_content here is actually the error message
	
	jobs = []
	for line in crontab_content.split("\n"):
		line = line.strip()
		if line and not line.startswith("#"):
			parts = line.split(maxsplit=5)
			if len(parts) < 6:
				return False, f"Linha de crontab inválida: {line}"
			schedule, command = ' '.join(parts[:5]), parts[5]
			jobs.append({
				"schedule": schedule,
				"command": command
			})
	
	return True, jobs