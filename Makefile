build:
	docker-compose build

rebuild:
	docker-compose up -d --build

start:
	docker-compose up -d

stop:
	docker-compose down

log:
	docker-compose logs -f

remove:
	docker-compose down -v --rmi local
