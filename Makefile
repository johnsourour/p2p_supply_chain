PORT ?= 8000

.PHONY: deps
deps: ## Install dependencies with the pipenv
	pipenv install -r requirements.txt

.PHONY: runiface
runiface: ## Run web-server interface
	pipenv run flask run --port $(PORT)

.PHONY: runbc
runbc: ## Run blockchain service
ifneq ($(PORT),8000)
	APPLICATION_SERVICES_ANNONCE="http://localhost:8000" \
	APPLICATION_PORT=$(PORT) pipenv run python node_server.py
else
	APPLICATION_PORT=$(PORT) pipenv run python node_server.py
endif

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
