build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

build_prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml build

up_prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

down_prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml down