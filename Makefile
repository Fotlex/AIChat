ENV=prod

COMPOSE_FILE = .docker/docker-compose.prod.yaml
DEV_COMPOSE_FILE = .docker/docker-compose.dev.yaml
ENV_FILE = .env
DOCKER_COMPOSE = docker compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE)
DEV_DOCKER_COMPOSE = docker compose -f $(DEV_COMPOSE_FILE) --env-file $(ENV_FILE)

-include $(ENV_FILE)


.PHONY: start_dev
start_dev:
	@echo "Start dev for $(ENV) environment..."
	@$(DEV_DOCKER_COMPOSE) up --build

.PHONY: dev
dev:
	@echo "Start dev for $(ENV) environment..."
	@$(DEV_DOCKER_COMPOSE) up

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\036m%-30s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "To use 'prod' environment, append 'ENV=prod' (e.g., make up ENV=prod)"


.PHONY: build
build:
	@echo "Building Docker images for $(ENV) environment..."
	@$(DOCKER_COMPOSE) build

.PHONY: up
up:
	@echo "Starting Docker containers for $(ENV) environment..."
	@$(DOCKER_COMPOSE) up -d

.PHONY: up-logs
up-logs:
	@echo "Starting Docker containers with logs for $(ENV) environment..."
	@$(DOCKER_COMPOSE) up

.PHONY: logs
logs:
	@$(DOCKER_COMPOSE) logs -f

.PHONY: down
down:
	@echo "Stopping and removing Docker containers for $(ENV) environment..."
	@$(DOCKER_COMPOSE) down

.PHONY: clean
clean:
	@echo "WARNING: This will remove ALL containers, images, and volumes for $(ENV) environment. Data will be lost."
	@bash -c 'read -p "Are you sure? (y/N) " confirm; \
 	if [ "$$confirm" = "y" ]; then \
		echo "Proceeding with clean for $(ENV) environment..."; \
  		$(DOCKER_COMPOSE) down --rmi all -v --volumes --remove-orphans; \
 	else \
  		echo "Clean operation cancelled."; \
  		exit 1; \
 	fi'

.PHONY: restart
restart:
	@echo "Restarting Docker containers for $(ENV) environment..."
	@$(DOCKER_COMPOSE) restart



.PHONY: migrate
migrate:
	@echo "Running migrations for $(ENV) environment..."
	@$(DOCKER_COMPOSE) exec web python backend/manage.py migrate --noinput

.PHONY: makemigrations
makemigrations:
	@$(DOCKER_COMPOSE) exec web python backend/manage.py makemigrations $(APP)


.PHONY: collectstatic
collectstatic:
	@echo "Collecting static files for $(ENV) environment..."
	@$(DOCKER_COMPOSE) exec app python backend/manage.py collectstatic --noinput


.PHONY: base_commands
base_commands:
	@echo "Collecting static files for $(ENV) environment..."
	@$(DOCKER_COMPOSE) exec web python backend/manage.py migrate --noinput
	@$(DOCKER_COMPOSE) exec web python backend/manage.py collectstatic --noinput
	@$(DOCKER_COMPOSE) exec web python backend/manage.py createsuperuser


.PHONY: super_user
super_user:
	@echo "Collecting static files for $(ENV) environment..."
	@$(DOCKER_COMPOSE) exec web python backend/manage.py createsuperuser
