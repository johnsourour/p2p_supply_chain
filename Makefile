PORT ?= 8000

.PHONY: deps
deps: ## Install dependencies with the pipenv
	pipenv install -r requirements.txt

.PHONY: run
run: ## Run blockchain service
ifneq ($(PORT),8000)
	APPLICATION_SERVICES_ANNONCE="http://localhost:8000" \
	APPLICATION_PORT=$(PORT) pipenv run python ./run.py
else
	APPLICATION_PORT=$(PORT) pipenv run python ./run.py
endif

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
