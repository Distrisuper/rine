.PHONY: build up down restart logs ps shell test test-ci test-local

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f --tail=200

ps:
	docker compose ps

shell:
	docker compose run --rm app /bin/sh

test:
	docker compose run --rm -e PYTHONPATH=/app test python -m pytest . -v

test-local:
	python -m pytest . -v

db-migrate:
	docker compose run --rm app alembic upgrade head