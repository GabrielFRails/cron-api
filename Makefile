venv:
	source .venv/bin/activate

api:
	uvicorn main:app --reload