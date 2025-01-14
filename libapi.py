from subprocess import run, PIPE, Popen

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

	jobs = []
	cron_lines = crontab_content.split("\n")
	for idx, line in enumerate(cron_lines):
		line = line.strip()
		if line and line.startswith("#cjid"):
			parts = line.split("%")
			prefix = parts[0]
			cjid = prefix.split(":")
			job = api_etl_crontab_line_todict(cron_lines[idx + 1])
			job['cjid'] = cjid
			jobs.append(job)

	if not len(jobs):
		return 0

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
	print(parts)
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

def api_cronjob_delete(user, id):
# {
	crontab_content = run_crontab_command(user)
	if not crontab_content:
		return 0

	found = False
	cron_lines = crontab_content.split("\n")
	for idx, line in enumerate(cron_lines):
		line = line.strip()
		if line and line.startswith("#cjid:"):
			parts = line.split("%")
			prefix = parts[0]
			cjid = prefix.split(":")
		
			if cjid == id:
				cron_lines.pop(idx)
				cron_lines.pop(idx+1)
				found = True
				break
	
	if not found:
		return -1
	
	new_crontab = "\n".join(cron_lines)
	p = Popen(['crontab', '-'], stdin=PIPE, stdout=PIPE, stderr=PIPE, text=True)
	stdout, stderr = p.communicate(input=new_crontab)

	if p.returncode != 0:
		return 0

	return 1
# }

def api_cronjob_update(user, id, updated_cron_job):
# {
	crontab_content = run_crontab_command(user)
	if not crontab_content:
		return 0

	found = False
	cron_lines = crontab_content.split("\n")
	for idx, line in enumerate(cron_lines):
		line = line.strip()
		if line and line.startswith("#cjid:"):
			parts = line.split("%")
			prefix = parts[0]
			cjid = prefix.split(":")
		
			if cjid == id:
				cron_lines[idx+1] = updated_cron_job
				found = True
				break

	if not found:
		return -1
	
	new_crontab = "\n".join(cron_lines)
	p = Popen(['crontab', '-'], stdin=PIPE, stdout=PIPE, stderr=PIPE, text=True)
	stdout, stderr = p.communicate(input=new_crontab)

	if p.returncode != 0:
		return 0

	return 1
# }