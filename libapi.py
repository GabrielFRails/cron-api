from subprocess import run, PIPE

def run_crontab_command(user: str) -> str | int:
# {
	try:
		result = run(['crontab', '-l', '-u', user], stdout=PIPE, stderr=PIPE, text=True, check=True)
		return result.stdout
	except:
		return 0
# }

def api_crontab_get(user: str) -> list[dict] | int:
# {
	crontab_content = run_crontab_command(user)
	if not crontab_content:
		return 0

	jobs = 0
	for line in crontab_content.split("\n"):
		line = line.strip()
		if line and not line.startswith("#"):
			parts = line.split(maxsplit=5)
			if len(parts) < 6:
				return 0

			schedule, command = ' '.join(parts[:5]), parts[5]
			jobs.append({
				"schedule": schedule,
				"command": command
			})

	return jobs
# }

def api_cronjob_get_by_id(user: str, id: str) -> dict | int:
# {
	crontab_content = run_crontab_command(user)
	if not crontab_content:
		return 0

	job = None
	cron_lines = crontab_content.split("\n")
	for idx, line in enumerate(cron_lines):
		line = line.strip()
		if line and line.startswith("#cjid:"):
			parts = line.split("%")
			prefix = parts[0]
			cjid = prefix.split(":")
		
			if cjid == id:
				job = api_etl_crontab_line_todict(cron_lines[idx + 1])
				job['cjid'] = cjid
				return job

	return 0
# }

def api_etl_crontab_line_todict(line):
# {
	parts = line.split(maxsplit=5)
	schedule, command = ' '.join(parts[:5]), parts[5]
	return {
		"schedule": schedule,
		"command": command
	}
# }	

def api_cronjob_add(user: str, cron_line: str) -> int:
# {
	current_crontab = run(["crontab", "-l", "-u", user], stdout=PIPE, stderr=PIPE, text=True)

	if current_crontab.returncode == 0:
		new_crontab = current_crontab.stdout + cron_line
	else:
		new_crontab = cron_line  # Caso não haja crontab atual

	p = Popen(['crontab', '-'], stdin=PIPE, stdout=PIPE, stderr=PIPE, text=True)
	stdout, stderr = p.communicate(input=new_crontab)

	if p.returncode != 0:
		return 0
		#return False, f"Erro ao atualizar crontab: {stderr}"

	return 1
# }	