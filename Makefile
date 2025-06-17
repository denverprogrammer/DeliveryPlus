init:
	docker compose -f docker-compose.deploy.yml run --rm ebcli init --profile packageparcels

create:
	docker compose -f docker-compose.deploy.yml run --rm ebcli create --profile packageparcels

deploy:
	docker compose -f docker-compose.deploy.yml run --rm ebcli deploy --profile packageparcels

status:
	docker compose -f docker-compose.deploy.yml run --rm ebcli status --profile packageparcels

nuke-it:
	docker compose down --remove-orphans --volumes
	docker volume prune --force
	docker network prune --force
	docker container prune --force
	docker rmi -f $(shell docker images -aq)

start:
	docker compose up --detach --build

destroy:
	docker compose down --remove-orphans --volumes
