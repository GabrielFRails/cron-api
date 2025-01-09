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

def api_cronjob_add(cron_line: str) -> tuple[bool, str]:
    current_crontab = run(["crontab", "-l"], stdout=PIPE, stderr=PIPE, text=True)

    if current_crontab.returncode == 0:
        new_crontab = current_crontab.stdout + cron_line
    else:
        new_crontab = cron_line  # Caso não haja crontab atual

    p = Popen(['crontab', '-'], stdin=PIPE, stdout=PIPE, stderr=PIPE, text=True)
    stdout, stderr = p.communicate(input=new_crontab)

    if p.returncode != 0:
        return False, f"Erro ao atualizar crontab: {stderr}"
    
    return True, "Cron job adicionado com sucesso"