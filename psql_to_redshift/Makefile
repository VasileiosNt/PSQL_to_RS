#!make 
include ./infrastructure/env/psql.env

.PHONY: help
help:
	@echo 'Usage:'
	@sed -n 's/^##//p' ${MAKEFILE_LIST} | column -t -s ':' |  sed -e 's/^/ /'


.PHONY: start-psql
start-psql:
	@docker-compose -f ./infrastructure/docker-compose-postgres.yaml up -d

.PHONY: stop-psql
stop-psql:
	@docker-compose -f ./infrastructure/docker-compose-postgres.yaml down

.PHONY: create-rs-cluster
create-rs-cluster:
	@echo "creating redshift cluster"
	@poetry run ansible-playbook ./infrastructure/redshift.yml


.PHONY: load-data-to-psql
load-data-to-psql:
	@poetry run python src/load_data.py

.PHONY: extract-table
extract-table:
	@echo 'Extracting table and saving it as gzip...'
	@psql -Atx postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}/${POSTGRES_DB} -c "COPY apps TO stdout DELIMITER ',' CSV HEADER "\ | gzip > ./assets/apps_data.csv.gzip
	@echo 'Done, file saved to assets.'

.PHONY: upload-to-s3
upload-to-s3:
	@poetry run python src/to_s3.py



.PHONY: get-uri-rs 
get-uri-rs:
	@echo 'Getting JDBC URI...'
	@$(eval RS_JDBC:=$(shell aws redshift describe-clusters --query 'Clusters[0].Endpoint.Address' --output text))
	@echo "RS_URI=${RS_JDBC}" >./infrastructure/env/rs_uri.env
	@echo ${RS_JDBC}

.PHONY: migrate-to-redshift
migrate-to-redshift:
	@echo 'Migrating data to redshift...'
	@poetry run python src/migrate_to_redshift.py

.phony: clean-up
clean-up:
	@echo 'Cleaning up...'
	@rm -rf ./assets/apps_data.csv.gzip
	@poetry run ansible-playbook ./infrastructure/del_redshift.yml
	@echo 'Done.'

.phony: install
install:
	@echo 'Installing dependencies'
	@poetry install
