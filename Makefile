DOCKER_COMPOSE = docker-compose
ENV ?= dev
CONTAINER_NAME = ghibli_api

DOCKER_COMPOSE_FILE = docker-compose.$(ENV).yml

.PHONY: all build up down clean restart logs test validate-env

all: help

##   help                  | Show this text
help: Makefile
	@sed -n 's/^##//p' $< | cat

validate-env:
	@if [ "$(ENV)" != "dev" ] && [ "$(ENV)" != "prd" ]; then \
		echo "Error: ENV must be either 'dev' or 'prd'"; \
		exit 1; \
	fi

##---------------------------------------------------
##   Application Commands
##---------------------------------------------------
##   build ENV=[dev|prd]   | Build the application
build: validate-env
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) up --build --force-recreate --remove-orphans

##   up ENV=[dev|prd]      | Build and start the application
up: validate-env
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) up -d

##   down ENV=[dev|prd]    | Stop the application
down: validate-env
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) down

##   ps ENV=[dev|prd|all]   | Lists containers (dev, prd, or all)
ps:
	@if [ "$(ENV)" = "all" ]; then \
		echo "\nDevelopment environment containers:"; \
		$(DOCKER_COMPOSE) -f docker-compose.dev.yml ps; \
		echo "\nProduction environment containers:"; \
		$(DOCKER_COMPOSE) -f docker-compose.prd.yml ps; \
	elif [ "$(ENV)" = "dev" ] || [ "$(ENV)" = "prd" ]; then \
		echo "\n$(ENV) environment containers:"; \
		$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) ps; \
	else \
		echo "Error: ENV must be 'dev', 'prd', or 'all'"; \
		exit 1; \
	fi

##   clean ENV=[dev|prd]   | Down and Remove images
clean: validate-env
	@echo "Cleaning $(ENV) environment..."
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) down -v --rmi all --remove-orphans

##   clean-all             | Clean both environments
clean-all:
	@echo "Cleaning development environment..."
	$(DOCKER_COMPOSE) -f docker-compose.dev.yml down -v --rmi all --remove-orphans
	@echo "Cleaning production environment..."
	$(DOCKER_COMPOSE) -f docker-compose.prd.yml down -v --rmi all --remove-orphans

##   restart ENV=[dev|prd] | Restart the application
restart: down up

##   logs ENV=[dev|prd]    | Show logs of the application
logs: validate-env
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) logs -f

##   logs_api ENV=[dev|prd]| Show logs of the API
logs_api: validate-env
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) logs -f $(CONTAINER_NAME)

##---------------------------------------------------
##   Dependencies
##---------------------------------------------------
##   requirements          | Install Python dependencies
requirements: validate-env
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) run --rm $(CONTAINER_NAME) pip install -r requirements.txt

##   requirements-test     | Install test dependencies
requirements-test: validate-env
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) run --rm $(CONTAINER_NAME) pip install -r requirements_test.txt

##---------------------------------------------------
##   Database Commands
##---------------------------------------------------
##   upgrade ENV=[dev|prd] | Run DB upgrade
upgrade: validate-env
	if [ -z $(id) ]; then \
		$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) run --rm $(CONTAINER_NAME) alembic upgrade head; \
	else \
		$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) run --rm $(CONTAINER_NAME) alembic upgrade $(id); \
	fi

##   downgrade ENV=[dev|prd]| Run DB downgrade
downgrade: validate-env
	if [ -z $(id) ]; then \
		$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) run --rm $(CONTAINER_NAME) alembic downgrade base; \
	else \
		$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) run --rm $(CONTAINER_NAME) alembic downgrade $(id); \
	fi

##   revision ENV=[dev|prd] msg="first" | Run DB revision. Set 'msg' arg.
revision: validate-env
	if [ -z $(msg) ]; then \
		echo "Especifique un mensaje para la migracion."; \
		return 1; \
	else \
		$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) run --rm $(CONTAINER_NAME) alembic db stamp head; \
		$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) run --rm $(CONTAINER_NAME) alembic revision --autogenerate -m $(msg); \
	fi

##---------------------------------------------------
##   Testing Commands (Development Only)
##---------------------------------------------------
validate-dev-only:
	@if [ "$(ENV)" = "prd" ]; then \
		echo "Error: This command is only available in development environment"; \
		exit 1; \
	fi

##   lint                  | Run pre-commit hooks (dev only)
lint: validate-dev-only
	pre-commit run --all-files && sudo chown -R $USER:$USER .

##   test                  | Run tests - use path=./tests/path for specific tests (dev only)
test: validate-dev-only
	$(DOCKER_COMPOSE) -f docker-compose.dev.yml build --build-arg TEST_MODE=1 $(CONTAINER_NAME)
	if [ -z $(path) ]; then \
		echo "Ejecutando la bateria completa de pruebas ..."; \
		$(DOCKER_COMPOSE) -f docker-compose.dev.yml run --rm $(CONTAINER_NAME) pytest -s -v app tests; \
	else \
		echo "Ejecutando los tests en $(path) ..."; \
		$(DOCKER_COMPOSE) -f docker-compose.dev.yml run --rm $(CONTAINER_NAME) pytest -s -v $(path); \
	fi

##   test-cov             | Run tests with coverage report (dev only)
test-cov: validate-dev-only
	$(DOCKER_COMPOSE) -f docker-compose.dev.yml build --build-arg TEST_MODE=1 $(CONTAINER_NAME)
	$(DOCKER_COMPOSE) -f docker-compose.dev.yml run --rm $(CONTAINER_NAME) pytest -v --cov=app tests/