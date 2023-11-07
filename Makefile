# Define docker compose command
DC := docker compose

# Default action when you just call `make`
all: up

# <BASIC DOCKER COMPOSE COMMANDS> ###########################

shell:
	@echo "Opening shell in python container..."
	$(DC) run --rm py bash

up:
	@echo "Bringing up all services..."
	$(DC) up -d

down:
	@echo "Taking down all services but keepingn the volumes (persistent data)..."
	$(DC) down

nuke:
	@echo "Nuking all services and volumes, deleting all docker-managed data..."
	$(DC) down -v --remove-orphans

logs:
	@echo "Tailing logs of all services..."
	$(DC) logs -f

logs-py:
	@echo "Tailing logs of the python service..."
	$(DC) logs -f py

# should only be necessary once, or when you change the Dockerfile or install new packages,
# since docker compose will mount the local files as a volume
build:
	@echo "Building python image..."
	$(DC) build py

# </BASIC DOCKER COMPOSE COMMANDS> ###########################

# <PYTHON UTILITY COMMANDS> ##################################

# run this to freeze new versions of packages / upgrade or to add a new package
# then run `make build` to build the new image
pip-compile:
	@echo "Compiling python requirements.in to requirements.txt..."
	$(DC) run --rm py pip-compile requirements/requirements.in --output-file=requirements/requirements.txt

# </PYTHON UTILITY COMMANDS> #################################

.PHONY: up down nuke all logs
