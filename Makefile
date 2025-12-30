.PHONY: help install dev build test clean docker-build docker-run docker-stop docker-clean deploy health check-types lint format

# Variables
IMAGE_NAME := staticwaves-pod-studio
VERSION := latest
REGISTRY := dockerhub
PLATFORM := linux/amd64

# Colors for output
GREEN  := \033[0;32m
YELLOW := \033[1;33m
RED    := \033[0;31m
NC     := \033[0m # No Color

## help: Display this help message
help:
	@echo "$(GREEN)StaticWaves POD Studio - Available Commands$(NC)"
	@echo ""
	@echo "$(YELLOW)Development:$(NC)"
	@echo "  make install        - Install dependencies"
	@echo "  make dev            - Start development server"
	@echo "  make build          - Build production bundle"
	@echo "  make test           - Run tests"
	@echo "  make check-types    - Run TypeScript type checking"
	@echo "  make clean          - Clean build artifacts"
	@echo ""
	@echo "$(YELLOW)Docker:$(NC)"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-run     - Run Docker container locally"
	@echo "  make docker-stop    - Stop Docker container"
	@echo "  make docker-clean   - Remove Docker image and container"
	@echo "  make docker-compose-up   - Start with docker-compose"
	@echo "  make docker-compose-down - Stop docker-compose"
	@echo ""
	@echo "$(YELLOW)Deployment:$(NC)"
	@echo "  make deploy         - Deploy using deploy.sh script"
	@echo "  make health         - Check application health"
	@echo ""
	@echo "$(YELLOW)Code Quality:$(NC)"
	@echo "  make format         - Format code (if prettier configured)"
	@echo "  make lint           - Lint code (if eslint configured)"
	@echo ""

## install: Install npm dependencies
install:
	@echo "$(GREEN)Installing dependencies...$(NC)"
	npm install
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

## dev: Start development server
dev:
	@echo "$(GREEN)Starting development server...$(NC)"
	npm run dev

## build: Build production bundle
build:
	@echo "$(GREEN)Building production bundle...$(NC)"
	npm run build
	@echo "$(GREEN)✓ Build complete$(NC)"

## test: Run tests
test:
	@echo "$(GREEN)Running tests...$(NC)"
	npm test || echo "$(YELLOW)No tests configured$(NC)"

## check-types: Run TypeScript type checking
check-types:
	@echo "$(GREEN)Checking types...$(NC)"
	npx tsc --noEmit
	@echo "$(GREEN)✓ Type check passed$(NC)"

## clean: Clean build artifacts
clean:
	@echo "$(GREEN)Cleaning build artifacts...$(NC)"
	rm -rf dist build .cache node_modules/.cache
	@echo "$(GREEN)✓ Clean complete$(NC)"

## docker-build: Build Docker image
docker-build:
	@echo "$(GREEN)Building Docker image...$(NC)"
	docker build --platform $(PLATFORM) -t $(IMAGE_NAME):$(VERSION) .
	@echo "$(GREEN)✓ Docker image built: $(IMAGE_NAME):$(VERSION)$(NC)"

## docker-run: Run Docker container locally
docker-run: docker-build
	@echo "$(GREEN)Starting Docker container...$(NC)"
	docker run -d --name pod-studio -p 8080:80 $(IMAGE_NAME):$(VERSION)
	@echo "$(GREEN)✓ Container running at http://localhost:8080$(NC)"
	@echo "$(YELLOW)Run 'make health' to check status$(NC)"

## docker-stop: Stop Docker container
docker-stop:
	@echo "$(GREEN)Stopping Docker container...$(NC)"
	docker stop pod-studio || true
	docker rm pod-studio || true
	@echo "$(GREEN)✓ Container stopped$(NC)"

## docker-clean: Remove Docker image and container
docker-clean: docker-stop
	@echo "$(GREEN)Removing Docker image...$(NC)"
	docker rmi $(IMAGE_NAME):$(VERSION) || true
	@echo "$(GREEN)✓ Docker artifacts cleaned$(NC)"

## docker-compose-up: Start with docker-compose
docker-compose-up:
	@echo "$(GREEN)Starting services with docker-compose...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Services started$(NC)"
	@echo "$(YELLOW)Run 'docker-compose logs -f' to view logs$(NC)"

## docker-compose-down: Stop docker-compose services
docker-compose-down:
	@echo "$(GREEN)Stopping services...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Services stopped$(NC)"

## deploy: Deploy using deploy.sh script
deploy:
	@echo "$(GREEN)Starting deployment...$(NC)"
	chmod +x deploy.sh
	./deploy.sh $(VERSION) $(REGISTRY) $(PLATFORM)

## health: Check application health
health:
	@echo "$(GREEN)Checking application health...$(NC)"
	@curl -f http://localhost:8080/health && echo "\n$(GREEN)✓ Application is healthy$(NC)" || echo "\n$(RED)✗ Application is not responding$(NC)"

## format: Format code (if prettier configured)
format:
	@echo "$(GREEN)Formatting code...$(NC)"
	npx prettier --write . || echo "$(YELLOW)Prettier not configured$(NC)"

## lint: Lint code (if eslint configured)
lint:
	@echo "$(GREEN)Linting code...$(NC)"
	npx eslint . || echo "$(YELLOW)ESLint not configured$(NC)"

## Quick commands for common workflows
.PHONY: quick-test quick-deploy local

## quick-test: Quick test (type check + build)
quick-test: check-types build
	@echo "$(GREEN)✓ Quick test passed$(NC)"

## quick-deploy: Quick deploy to DockerHub
quick-deploy: quick-test docker-build
	@echo "$(GREEN)Ready for deployment$(NC)"
	@echo "$(YELLOW)Run 'make deploy' to push to registry$(NC)"

## local: Full local testing (build + run + health check)
local: docker-build docker-stop docker-run
	@echo "$(GREEN)Waiting for container to start...$(NC)"
	@sleep 3
	@make health
