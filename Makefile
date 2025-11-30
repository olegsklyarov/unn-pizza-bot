VENV_DIR = .venv
ACTIVATE_VENV := . $(VENV_DIR)/bin/activate

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

test: black ruff


#
# Docker commands
#

DOCKER_NETWORK=pizza_bot_network

POSTGRES_VOLUME=postgres_data
POSTGRES_CONTAINER=postgres_17

REDIS_VOLUME=redis_data
REDIS_CONTAINER=redis_7

BOT_IMAGE=olegsklyarov/unn_pizza_bot
BOT_CONTAINER=pizza_bot

# Автоматически загружаем переменные из .env
include .env
export $(shell sed 's/=.*//' .env)

docker_volume:
	docker volume create $(POSTGRES_VOLUME) || true
	docker volume create $(REDIS_VOLUME) || true

docker_net:
	docker network create $(DOCKER_NETWORK) || true

postgres_run: docker_volume docker_net
	docker run -d \
	  --name $(POSTGRES_CONTAINER) \
	  -e POSTGRES_USER="$(POSTGRES_USER)" \
	  -e POSTGRES_PASSWORD="$(POSTGRES_PASSWORD)" \
	  -e POSTGRES_DB="$(POSTGRES_DATABASE)" \
	  -p "$(POSTGRES_PORT_HOST):$(POSTGRES_PORT_CONTAINER)" \
	  -v $(POSTGRES_VOLUME):/var/lib/postgresql/data \
	  --health-cmd="pg_isready -U $(POSTGRES_USER)" \
	  --health-interval=10s \
	  --health-timeout=5s \
	  --health-retries=5 \
	  --network $(DOCKER_NETWORK) \
	  postgres:17

postgres_stop:
	docker stop $(POSTGRES_CONTAINER)
	docker rm $(POSTGRES_CONTAINER)

redis_run: docker_volume docker_net
	docker run -d \
	  --name $(REDIS_CONTAINER) \
	  -p "$(REDIS_PORT_HOST):$(REDIS_PORT_CONTAINER)" \
	  -v $(REDIS_VOLUME):/data \
	  --network $(DOCKER_NETWORK) \
	  redis:7-alpine \
	  redis-server --save 20 1

redis_stop:
	docker stop $(REDIS_CONTAINER)
	docker rm $(REDIS_CONTAINER)

build:
	docker build \
	  -t $(BOT_IMAGE) \
	  --platform linux/amd64,linux/arm64 \
	  -f Dockerfile \
	  .

push:
	docker push $(BOT_IMAGE)

run: docker_net
	docker run -d \
	  --name $(BOT_CONTAINER) \
	  --restart unless-stopped \
	  -e POSTGRES_HOST="$(POSTGRES_CONTAINER)" \
	  -e POSTGRES_PORT="$(POSTGRES_PORT_CONTAINER)" \
	  -e POSTGRES_USER="$(POSTGRES_USER)" \
	  -e POSTGRES_PASSWORD="$(POSTGRES_PASSWORD)" \
	  -e POSTGRES_DATABASE="$(POSTGRES_DATABASE)" \
	  -e REDIS_URL="$(REDIS_URL)" \
	  -e TELEGRAM_TOKEN="$(TELEGRAM_TOKEN)" \
	  -e YOOKASSA_TOKEN="$(YOOKASSA_TOKEN)" \
	  --network $(DOCKER_NETWORK) \
	  $(BOT_IMAGE)

stop:
	docker stop $(BOT_CONTAINER)
	docker rm $(BOT_CONTAINER)

logs:
	docker logs -f $(BOT_CONTAINER)
