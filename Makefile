.PHONY: help setup dev build clean deploy-gcp

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Initial project setup
	@echo "Setting up project..."
	@chmod +x scripts/setup.sh
	@./scripts/setup.sh

dev: ## Start development environment with Docker Compose
	docker-compose up --build

dev-frontend: ## Start frontend development server
	cd frontend && npm run dev

dev-backend: ## Start backend development server
	cd backend && source venv/bin/activate && uvicorn app.main:app --reload

build: ## Build Docker images
	docker-compose build

clean: ## Clean up containers and images
	docker-compose down -v
	docker system prune -f

test-frontend: ## Run frontend tests
	cd frontend && npm run lint && npm run build

test-backend: ## Run backend tests
	cd backend && source venv/bin/activate && pytest

lint: ## Run linters
	cd frontend && npm run lint
	cd backend && flake8 app --max-line-length=120

deploy-gcp: ## Deploy to Google Cloud Platform
	@chmod +x scripts/deploy-gcp.sh
	@./scripts/deploy-gcp.sh

tf-init: ## Initialize Terraform
	cd terraform && terraform init

tf-plan: ## Plan Terraform changes
	cd terraform && terraform plan

tf-apply: ## Apply Terraform configuration
	cd terraform && terraform apply

tf-destroy: ## Destroy Terraform resources
	cd terraform && terraform destroy

logs-backend: ## View backend logs (GCP)
	gcloud run logs read ai-diary-backend --limit=50

logs-frontend: ## View frontend logs (GCP)
	gcloud run logs read ai-diary-frontend --limit=50

status: ## Check GCP service status
	gcloud run services list


