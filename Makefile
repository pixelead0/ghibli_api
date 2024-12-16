DOCKER_COMPOSE = docker-compose
DOCKER_COMPOSE_FILE = docker-compose.yml
CONTAINER_NAME = ghibli_api

.PHONY: all build up down clean restart logs test

all: help

##   help                  | Show this text
help: Makefile
	@sed -n 's/^##//p' $< | cat

##---------------------------------------------------
##   build                 | Build the application
build:
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) up --build --force-recreate --remove-orphans

##   up                   | Build and start the application
up:
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) up -d

##   down                 | Stop the application
down:
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) down

##   ps                   | Lists containers
ps:
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) ps

##   clean                | Down and Remove images
clean:
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) down -v --rmi all --remove-orphans

##   restart              | Restart the application
restart: down up

##   logs                 | Show logs of the application
logs:
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) logs -f

##   logs_api             | Show logs of the application
logs_api:
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) logs -f $(CONTAINER_NAME)

##---------------------------------------------------
##   requirements         | pip install -r requirements.txt
requirements:
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE)  run --rm $(CONTAINER_NAME) pip install -r requirements.txt

##---------------------------------------------------
##   upgrade              | Run DB upgrade
upgrade:
	if [ -z $(id) ]; then \
		$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE)  run --rm $(CONTAINER_NAME) alembic upgrade head; \
	else \
		$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE)  run --rm $(CONTAINER_NAME) alembic upgrade $(id); \
	fi

##   downgrade            | Run DB downgrade
downgrade:
	if [ -z $(id) ]; then \
		$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) run --rm $(CONTAINER_NAME) alembic downgrade base; \
	else \
		$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) run --rm $(CONTAINER_NAME) alembic downgrade $(id); \
	fi

##   revision msg="first" | Run DB revision. Set 'msg' arg.
revision:
	if [ -z $(msg) ]; then \
		echo "Especifique un mensaje para la migracion."; \
		return 1; \
	else \
		$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) run --rm $(CONTAINER_NAME) alembic db stamp head; \
		$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) run --rm $(CONTAINER_NAME) alembic revision --autogenerate -m $(msg); \
	fi

##---------------------------------------------------
##   lint                 | Exec pre-commit
lint:
	pre-commit run --all-files  && sudo chown -R $USER:$USER .

##---------------------------------------------------
##   test                 | Run tests
test:
	if [ -z $(path) ]; then \
		echo "Ejecutando la bateria de pruebas ..."; \
		$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) run --rm $(CONTAINER_NAME) pytest -s -v app tests; \
	else \
		echo "Ejecutando los tests en $(path) ..."; \
		$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) run --rm $(CONTAINER_NAME) pytest -s -v $(path); \
	fi

