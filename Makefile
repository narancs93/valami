# Set default environment to 'local' if none is provided
ENV ?= local

# Default target: show available commands when no target is specified
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make up ENV=local|prod                            - Bring up the services with Docker Compose (--build)"
	@echo "  make down ENV=local|prod                          - Bring down the services"
	@echo "  make createsuperuser ENV=local|prod               - Create a Django superuser"
	@echo "  make makemigrations ENV=local|prod                - Make Django migrations"
	@echo "  make migrate ENV=local|prod                       - Apply Django migrations"
	@echo "  make shell ENV=local|prod                         - Start Django shell"
	@echo "  make create_tenant ENV=local|prod                 - Create tenant"
	@echo "  make create_tenant_superuser ENV=local|prod       - Create tenant"
	@echo "  make pytest                                       - Run pytest for unit testing (local)"
	@echo "  make coverage                                     - Run tests with coverage collection (local)"
	@echo "  make coverage-report                              - Generate and display coverage report (local)"


# Command to bring up the services with --build option based on the environment
up:
ifeq ($(ENV),local)
	@docker compose -f docker-compose.local.yaml up --build -d
else ifeq ($(ENV),prod)
	@docker compose -f docker-compose.production.yaml up --build -d
else
	@echo "Invalid ENV value! Please specify ENV=local or ENV=prod."
	exit 1
endif

# Command to bring down the services based on the environment
down:
ifeq ($(ENV),local)
	@docker compose -f docker-compose.local.yaml down
else ifeq ($(ENV),prod)
	@docker compose -f docker-compose.production.yaml down
else
	@echo "Invalid ENV value! Please specify ENV=local or ENV=prod."
	exit 1
endif

# Command to run createsuperuser with the appropriate docker-compose file
createsuperuser:
ifeq ($(ENV),local)
	@docker compose -f docker-compose.local.yaml run --rm django python manage.py createsuperuser
else ifeq ($(ENV),prod)
	@docker compose -f docker-compose.production.yaml run --rm django python manage.py createsuperuser
else
	@echo "Invalid ENV value! Please specify ENV=local or ENV=prod."
	exit 1
endif

makemigrations:
ifeq ($(ENV),local)
	@docker compose -f docker-compose.local.yaml run --rm django python manage.py makemigrations
else ifeq ($(ENV),prod)
	@docker compose -f docker-compose.production.yaml run --rm django python manage.py makemigrations
else
	@echo "Invalid ENV value! Please specify ENV=local or ENV=prod."
	exit 1
endif

# Command to run migrate with the appropriate docker-compose file
migrate:
ifeq ($(ENV),local)
	@docker compose -f docker-compose.local.yaml run --rm django python manage.py migrate
else ifeq ($(ENV),prod)
	@docker compose -f docker-compose.production.yaml run --rm django python manage.py migrate
else
	@echo "Invalid ENV value! Please specify ENV=local or ENV=prod."
	exit 1
endif

# Command to run Django shell with the appropriate docker-compose file
shell:
ifeq ($(ENV),local)
	@docker compose -f docker-compose.local.yaml run --rm django python manage.py shell
else ifeq ($(ENV),prod)
	@docker compose -f docker-compose.production.yaml run --rm django python manage.py shell
else
	@echo "Invalid ENV value! Please specify ENV=local or ENV=prod."
	exit 1
endif

# Command to run create_tenant with the appropriate docker-compose file
create_tenant:
ifeq ($(ENV),local)
	@docker compose -f docker-compose.local.yaml run --rm django python manage.py create_tenant
else ifeq ($(ENV),prod)
	@docker compose -f docker-compose.production.yaml run --rm django python manage.py create_tenant_superuser
else
	@echo "Invalid ENV value! Please specify ENV=local or ENV=prod."
	exit 1
endif

# Command to run create_tenant_superuser with the appropriate docker-compose file
create_tenant_superuser:
ifeq ($(ENV),local)
	@docker compose -f docker-compose.local.yaml run --rm django python manage.py create_tenant_superuser
else ifeq ($(ENV),prod)
	@docker compose -f docker-compose.production.yaml run --rm django python manage.py create_tenant_superuser
else
	@echo "Invalid ENV value! Please specify ENV=local or ENV=prod."
	exit 1
endif

# Command to run pytest for unit testing
pytest:
	@docker compose -f docker-compose.local.yaml run --rm django pytest

# Command to run pytest with coverage for test coverage analysis
coverage:
	@docker compose -f docker-compose.local.yaml run --rm django coverage run -m pytest

# Command to generate and display a test coverage report
coverage-report:
	@docker compose -f docker-compose.local.yaml run --rm django coverage report

# Command to bring up keycloak service
keycloak:
	@docker compose -f docker-compose.keycloak.yaml -p keycloak up --build -d

# Command to bring down keycloak service
keycloak_down:
	@docker compose -f docker-compose.keycloak.yaml -p keycloak down