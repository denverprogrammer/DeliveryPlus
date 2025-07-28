# =============================================================================
# DeliveryPlus Development & Deployment Commands
# =============================================================================

.PHONY: help init create deploy status nuke-it start destroy dev prod stop-ergo quick-start

# Default target
help: ## Show this help message
	@echo "🚀 DeliveryPlus Development & Deployment"
	@echo "========================================"
	@echo ""
	@echo "Development Commands:"
	@echo "  make dev          - Start development with custom domains"
	@echo "  make quick-start  - Quick setup with prerequisites check"
	@echo "  make stop-ergo    - Stop Ergo proxy"
	@echo ""
	@echo "Production Commands:"
	@echo "  make prod         - Start production environment"
	@echo "  make start        - Start standard development environment"
	@echo "  make destroy      - Stop all containers"
	@echo ""
	@echo "AWS Elastic Beanstalk Commands:"
	@echo "  make init         - Initialize EB CLI"
	@echo "  make create       - Create EB environment"
	@echo "  make deploy       - Deploy to EB"
	@echo "  make status       - Check EB status"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make nuke-it      - Clean up all Docker resources"
	@echo "  make logs         - View logs"
	@echo "  make logs-follow  - Follow logs"
	@echo ""
	@echo "🌐 Development Domains:"
	@echo "  Main App:     http://deliveryplus.local"
	@echo "  Admin:        http://admin.local"
	@echo "  Management:   http://mgmt.local"
	@echo "  Tracking:     http://tracking.local"
	@echo "  API:          http://api.local"

# =============================================================================
# Development Commands
# =============================================================================

dev: ## Start development with custom domains (Ergo + nginx)
	@echo "📦 Setting up development environment with custom domains..."
	@cp nginx.conf nginx.conf.current
	@docker compose down
	@docker compose up --build -d
	@echo "🚀 Starting Ergo proxy..."
	@if [ -f .ergo.pid ]; then \
		kill $$(cat .ergo.pid) 2>/dev/null || true; \
		rm .ergo.pid; \
	fi
	@if lsof -ti:2000 > /dev/null 2>&1; then \
		echo "🛑 Port 2000 is in use. Stopping existing process..."; \
		kill $$(lsof -ti:2000) 2>/dev/null || true; \
		sleep 2; \
	fi
	@ergo run --domain .local &
	@echo $$! > .ergo.pid
	@echo "✅ Development environment deployed!"
	@echo ""
	@echo "🌐 Custom Domain Access:"
	@echo "   Main App:     http://deliveryplus.local"
	@echo "   Admin:        http://admin.local"
	@echo "   Management:   http://mgmt.local"
	@echo "   Tracking:     http://tracking.local"
	@echo "   API:          http://api.local"
	@echo ""
	@echo "💡 If domains don't resolve, add to /etc/hosts:"
	@echo "   127.0.0.1 deliveryplus.local admin.local mgmt.local tracking.local api.local"
	@echo ""
	@echo "💡 Ergo proxy running"
	@echo "   To stop Ergo: make stop-ergo"

quick-start: ## Quick setup with prerequisites check
	@echo "🚀 Quick Start for DeliveryPlus Development"
	@echo "=========================================="
	@if ! command -v ergo &> /dev/null; then \
		echo "❌ Ergo is not installed. Installing..."; \
		if command -v brew &> /dev/null; then \
			brew install ergo; \
		else \
			echo "❌ Homebrew not found. Please install Ergo manually:"; \
			echo "   https://github.com/ergo-services/ergo/releases"; \
			exit 1; \
		fi; \
	fi
	@if ! docker info &> /dev/null; then \
		echo "❌ Docker is not running. Please start Docker and try again."; \
		exit 1; \
	fi
	@echo "✅ Prerequisites check passed"
	@echo ""
	@echo "📦 Deploying development environment..."
	@$(MAKE) dev
	@echo ""
	@echo "🎉 Setup Complete!"
	@echo "=================="
	@echo ""
	@echo "🌐 Access your application:"
	@echo "   Main App:     http://deliveryplus.local"
	@echo "   Admin:        http://admin.local"
	@echo "   Management:   http://mgmt.local"
	@echo "   Tracking:     http://tracking.local"
	@echo "   API:          http://api.local"
	@echo ""
	@echo "📊 Check status: make status-dev"
	@echo "🛑 Stop Ergo:   make stop-ergo"
	@echo "❌ Stop all:     make destroy"
	@echo ""
	@echo "💡 Tips:"
	@echo "   - Changes to code are reflected immediately"
	@echo "   - Check logs with: make logs-follow"



stop-ergo: ## Stop Ergo proxy
	@if [ -f .ergo.pid ]; then \
		ERGO_PID=$$(cat .ergo.pid); \
		if ps -p $$ERGO_PID > /dev/null 2>&1; then \
			echo "🛑 Stopping Ergo proxy (PID: $$ERGO_PID)..."; \
			kill $$ERGO_PID; \
			rm .ergo.pid; \
			echo "✅ Ergo proxy stopped"; \
		else \
			echo "❌ Ergo proxy not running"; \
			rm .ergo.pid; \
		fi; \
	else \
		echo "❌ No Ergo PID file found"; \
	fi
	@if lsof -ti:2000 > /dev/null 2>&1; then \
		echo "🛑 Stopping any process on port 2000..."; \
		kill $$(lsof -ti:2000) 2>/dev/null || true; \
		echo "✅ Port 2000 cleared"; \
	fi

# =============================================================================
# Production Commands
# =============================================================================

prod: ## Start production environment
	@echo "🚀 Setting up production environment..."
	@cp nginx.conf.production nginx.conf.current
	@docker compose down
	@docker compose up --build -d
	@echo "✅ Production environment deployed!"
	@echo "🌐 Access your application at: http://localhost"
	@echo "🔧 Admin interface: http://localhost/admin/"
	@echo "📊 Management API: http://localhost/mgmt/"
	@echo "📦 Tracking API: http://localhost/tracking/"
	@echo "🔌 General API: http://localhost/api/"

start: ## Start standard development environment
	@docker compose up --detach --build

destroy: ## Stop all containers
	@docker compose down --remove-orphans --volumes

# =============================================================================
# AWS Elastic Beanstalk Commands
# =============================================================================

init: ## Initialize EB CLI
	docker compose -f docker-compose.deploy.yml run --rm ebcli init --profile packageparcels

create: ## Create EB environment
	docker compose -f docker-compose.deploy.yml run --rm ebcli create --profile packageparcels

deploy: ## Deploy to EB
	docker compose -f docker-compose.deploy.yml run --rm ebcli deploy --profile packageparcels

status: ## Check EB status
	docker compose -f docker-compose.deploy.yml run --rm ebcli status --profile packageparcels

# =============================================================================
# Utility Commands
# =============================================================================

nuke-it: ## Clean up all Docker resources
	@echo "🧹 Cleaning up all Docker resources..."
	@docker compose down --remove-orphans --volumes
	@docker volume prune --force
	@docker network prune --force
	@docker container prune --force
	@docker rmi -f $$(docker images -aq)
	@if [ -f .ergo.pid ]; then \
		kill $$(cat .ergo.pid) 2>/dev/null || true; \
		rm .ergo.pid; \
	fi
	@echo "✅ Cleanup complete!"

logs: ## View logs
	@docker compose logs

logs-follow: ## Follow logs
	@docker compose logs -f

# =============================================================================
# Status Commands
# =============================================================================

status-dev: ## Check development status
	@echo "📊 Current deployment status:"
	@docker compose ps
	@echo ""
	@echo "🔍 Recent logs:"
	@docker compose logs --tail=20
	@echo ""
	@echo "🌐 Ergo proxy status:"
	@if [ -f .ergo.pid ]; then \
		ERGO_PID=$$(cat .ergo.pid); \
		if ps -p $$ERGO_PID > /dev/null; then \
			echo "✅ Ergo proxy running (PID: $$ERGO_PID)"; \
			echo "🌐 Custom domains available:"; \
			echo "   http://deliveryplus.local"; \
			echo "   http://admin.local"; \
			echo "   http://mgmt.local"; \
			echo "   http://tracking.local"; \
			echo "   http://api.local"; \
		else \
			echo "❌ Ergo proxy not running"; \
		fi; \
	else \
		echo "❌ Ergo proxy not started"; \
	fi
