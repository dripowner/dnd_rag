.PHONY: run
run:
	uvicorn fastapi.main:app --reload --port 8000

.PHONY: build
build:
	docker-compose build

.PHONY: up
up:
	docker-compose up

.PHONY: down
down:
	docker-compose down

.PHONY: local
local:
	venv/Scripts/python.exe fastapi/main.py & venv/Scripts/streamlit.exe run streamlit/app.py
