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
	docker compose run --rm app python -m unittest discover -s tests

test-ci:
	docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm test

test-local:
	python -m unittest discover -s tests
