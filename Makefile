.PHONY: build
build:
	docker-compose -f docker-compose.yaml build
	docker-compose -f docker-compose.test.yaml build test

.PHONY: up
up:
	docker-compose -f docker-compose.yaml up

.PHONY: down
down:
	docker-compose -f docker-compose.yaml down

.PHONY: local
local:
	cd fastapi
	if [ ! -d "venv" ]; then \
		python -m venv venv; \
		./venv/Scripts/pip.exe install -r fastapi/requirements.txt; \
	fi
	cd ../streamlit
	if [ ! -d "venv" ]; then \
		python -m venv venv; \
		./venv/Scripts/pip.exe install -r streamlit/requirements.txt; \
	fi
	fastapi/venv/Scripts/python.exe fastapi/main.py & streamlit/venv/Scripts/streamlit.exe run streamlit/app.py

.PHONY: test-up
test-up:
	docker-compose -f docker-compose.test.yaml up -d fastapi
	sleep 10
	docker-compose -f docker-compose.test.yaml up test

.PHONY: test-down
test-down:
	docker-compose -f docker-compose.test.yaml down test
	docker-compose -f docker-compose.test.yaml down fastapi

.PHONY: test-dataset-upload
test-dataset-upload:
	docker-compose -f docker-compose.test.yaml up upload-dataset