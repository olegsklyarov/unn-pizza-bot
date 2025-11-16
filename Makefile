VENV_DIR = .venv
ACTIVATE_VENV := . $(VENV_DIR)/bin/activate

DOCKER_NETWORK=pizza_bot_network

POSTGRES_VOLUME=postgres_data
POSTGRES_CONTAINER=postgres_database

TELEGRAM_BOT_IMAGE=olegsklyarov/unn_pizza_bot
TELEGRAM_BOT_CONTAINER=telegram_pizza_bot

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
	docker volume create $(POSTGRES_VOLUME) || true

docker_network_create:
	docker network create $(DOCKER_NETWORK) || true

docker_postgres_start: docker_postgres_volume_create docker_network_create
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
	  --network $(DOCKER_NETWORK) \
	  postgres:17

docker_postgres_stop:
	docker stop $(POSTGRES_CONTAINER)
	docker rm $(POSTGRES_CONTAINER)

telegram_bot_build:
	docker build \
	  -t $(TELEGRAM_BOT_IMAGE) \
	  --platform linux/amd64,linux/arm64 \
	  -f Dockerfile \
	  .

telegram_bot_start: docker_postgres_volume_create
	docker run -d \
	  --name $(TELEGRAM_BOT_CONTAINER) \
	  --restart unless-stopped \
	  -e POSTGRES_HOST="$(POSTGRES_CONTAINER)" \
	  -e POSTGRES_PORT="5432" \
	  -e POSTGRES_USER="$(POSTGRES_USER)" \
	  -e POSTGRES_PASSWORD="$(POSTGRES_PASSWORD)" \
	  -e POSTGRES_DATABASE="$(POSTGRES_DATABASE)" \
	  -e TELEGRAM_TOKEN="$(TELEGRAM_TOKEN)" \
	  -e YOOKASSA_TOKEN="$(YOOKASSA_TOKEN)" \
	  --network $(DOCKER_NETWORK) \
	  $(TELEGRAM_BOT_IMAGE)

# Остановка и удаление Telegram Bot контейнера
telegram_bot_stop:
	docker stop $(TELEGRAM_BOT_CONTAINER)
	docker rm $(TELEGRAM_BOT_CONTAINER)

telegram_bot_push:
	docker push $(TELEGRAM_BOT_IMAGE)
