VENV_DIR = .venv
ACTIVATE_VENV := . $(VENV_DIR)/bin/activate

# Имя volume
POSTGRES_VOLUME=postgres_data
POSTGRES_CONTAINER=postgres_database

# Автоматически загружаем переменные из .env
include .env
export $(shell sed 's/=.*//' .env)

$(VENV_DIR):
	python3 -m venv $(VENV_DIR)
	$(ACTIVATE_VENV) && pip install --upgrade pip
	$(ACTIVATE_VENV) && pip install --requirement requirements.txt

install: $(VENV_DIR)

# Run black formatter
black: $(VENV_DIR)
	$(ACTIVATE_VENV) && black .

# Run ruff linter
ruff: $(VENV_DIR)
	$(ACTIVATE_VENV) && ruff check .

# Run pytest
pytest: $(VENV_DIR)
	$(ACTIVATE_VENV) && PYTHONPATH=. pytest

# Run all tests (includes black, ruff, and pytest)
test: black ruff pytest

docker_postgres_volume_create:
	docker volume create $(POSTGRES_VOLUME)

docker_postgres_start: docker_postgres_volume_create
	docker run -d \
	  --name $(POSTGRES_CONTAINER) \
	  -e POSTGRES_USER="$(POSTGRES_USER)" \
	  -e POSTGRES_PASSWORD="$(POSTGRES_PASSWORD)" \
	  -e POSTGRES_DB="$(POSTGRES_DATABASE)" \
	  -p "$(POSTGRES_PORT):5432" \
	  -v $(POSTGRES_VOLUME):/var/lib/postgresql/data \
	  --health-cmd="pg_isready -U $(POSTGRES_USER)" \
	  --health-interval=10s \
	  --health-timeout=5s \
	  --health-retries=5 \
	  postgres:17

docker_postgres_stop:
	docker stop $(POSTGRES_CONTAINER)
	docker rm $(POSTGRES_CONTAINER)
