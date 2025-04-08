init:
	docker compose -f docker-compose.deploy.yml run --rm ebcli init --profile deliveryplus

create:
	docker compose -f docker-compose.deploy.yml run --rm ebcli create --profile deliveryplus

deploy:
	docker compose -f docker-compose.deploy.yml run --rm ebcli deploy --profile deliveryplus

status:
	docker compose -f docker-compose.deploy.yml run --rm ebcli status --profile deliveryplus
