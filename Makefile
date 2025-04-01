build:
	docker-compose build

start:
	docker-compose up -d

stop:
	docker-compose down

log:
	docker-compose logs -f

remove:
	docker-compose down -v --rmi local

restart:
	docker-compose down
	docker-compose up -d --build

run_scripts:
	docker-compose -f docker-compose.init.yml up -d

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
	
run_scripts_prod:
	docker-compose -f docker-compose.init.yml up -d