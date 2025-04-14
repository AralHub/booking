build_dev:
	docker-compose build

start_dev:
	docker-compose up -d

stop_dev:
	docker-compose down

log_dev:
	docker-compose logs -f

remove_dev:
	docker-compose down -v --rmi local

restart_dev:
	docker-compose down
	docker-compose up -d --build

#========== PROD ==========#
build_prod:
	docker-compose -f docker-compose.prod.yml build

start_prod:
	docker-compose -f docker-compose.prod.yml up -d

stop_prod:
	docker-compose -f docker-compose.prod.yml down

log_prod:
	docker-compose -f docker-compose.prod.yml logs -f

remove_prod:
	docker-compose -f docker-compose.prod.yml down -v --rmi local

restart_prod:
	docker-compose -f docker-compose.prod.yml down
	docker-compose -f docker-compose.prod.yml up -d --build
	
