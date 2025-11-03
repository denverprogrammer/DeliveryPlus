# =============================================================================
# DeliveryPlus Development & Deployment Commands
# =============================================================================

.PHONY: help local-start local-stop quick-start docker-start docker-stop ergo-start ergo-stop ergo-check docker-check prod prod-config init create deploy status nuke-it docker-logs ergo-logs

ifeq ($(build),true)
BUILD_PARAM = --build --force-recreate
endif

DETACHED_PARAM = -d

ifeq ($(container-clean),true)
CONTAINER_CLEAN_PARAM = --remove-orphans
endif

ifeq ($(volume-clean),true)
VOLUME_CLEAN_PARAM = --volumes
endif

ifeq ($(follow),true)
FOLLOW_PARAM = -f
endif

ifeq ($(area),true)
AREA_PARAM = $(area)
endif

ifdef config
CONFIG_PARAM = $(config)
endif

# Default target
help: ## Show this help message
	@echo "🚀 DeliveryPlus Development & Deployment"
	@echo "========================================"
	@echo ""
	@echo "Development Commands:"
	@echo "  make local-start  - Start development with custom domains"
	@echo "  make local-stop   - Stop development environment"
	@echo "  make quick-start  - Quick setup with prerequisites check"
	@echo "  make docker-start - Start Docker containers only"
	@echo "  make docker-stop  - Stop Docker containers only"
	@echo ""
	@echo "Docker Parameters:"
	@echo "  container-clean=true - Remove containers when stopping"
	@echo "  volume-clean=true    - Remove volumes when stopping"
	@echo "  make ergo-start      - Start Ergo proxy only"
	@echo "  make ergo-stop       - Stop Ergo proxy only"
	@echo "  make ergo-check      - Check/install Ergo proxy"
	@echo "  make docker-check    - Check Docker status"
	@echo ""
	@echo "Production Commands:"
	@echo "  make prod         - Start production environment"
	@echo ""
	@echo "AWS Elastic Beanstalk Commands:"
	@echo "  make init         - Initialize EB CLI"
	@echo "  make create       - Create EB environment"
	@echo "  make deploy       - Deploy to EB"
	@echo "  make status       - Check EB status"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make nuke-it      - Clean up all Docker resources"
	@echo "  make docker-logs  - View Docker logs (area=web, follow=true)"
	@echo "  make ergo-logs    - View Ergo logs (follow=true)"
	@echo ""
	@echo "🌐 Development Domains:"
	@echo "  Delivery App:   http://deliveryplus.local (port 3000)"
	@echo "  Management App: http://mgmt.local (port 3001)"
	@echo "  Admin:          http://admin.local"

# =============================================================================
# Development Commands
# =============================================================================

local-start: ## Start development with custom domains
	@$(MAKE) docker-stop
	@$(MAKE) docker-start
	@$(MAKE) ergo-start
	@echo "✅ Development environment deployed!"
	@echo ""
	@echo "🌐 Custom Domain Access:"
	@echo "   Delivery App:  http://deliveryplus.local (port 3000)"
	@echo "   Management App: http://mgmt.local (port 3001)"
	@echo "   Admin:         http://admin.local"
	@echo ""
	@echo "💡 Ergo proxy running (headless)"
	@echo "   To stop Ergo: make ergo-stop"
	@echo "   To view logs: make ergo-logs"

local-stop: docker-stop ergo-stop ## Stop development environment
	@echo "✅ Development environment stopped!"
	@echo ""
	@echo "🛑 Docker containers stopped"
	@echo "🛑 Ergo proxy stopped"

docker-start: ## Start Docker containers only
	@echo "🐳 Starting Docker containers..."
	@docker compose up $(BUILD_PARAM) $(DETACHED_PARAM)

docker-stop: ## Stop Docker containers only
	@echo "🐳 Stopping Docker containers..."
	@docker compose down $(CONTAINER_CLEAN_PARAM) $(VOLUME_CLEAN_PARAM)

ergo-start: ## Start Ergo proxy only
	@echo "🚀 Starting Ergo proxy..."
	@echo "📊 Starting Ergo in detached mode (logs to ergo.log)..."
	@ergo run --domain .local > ergo.log 2>&1 &
	@echo $$! > .ergo.pid

ergo-stop: ## Stop Ergo proxy only
	@if [ -f .ergo.pid ]; then \
		ERGO_PID=$$(cat .ergo.pid); \
		if ps -p $$ERGO_PID > /dev/null 2>&1; then \
			echo "🛑 Stopping Ergo proxy (PID: $$ERGO_PID)..."; \
			kill $$ERGO_PID; \
		fi; \
		rm .ergo.pid; \
	fi
	@if lsof -ti:2000 > /dev/null 2>&1; then \
		for pid in $$(lsof -ti:2000); do \
			if ps -p $$pid -o comm= | grep -q ergo; then \
				echo "🛑 Stopping Ergo process (PID: $$pid)..."; \
				kill $$pid 2>/dev/null || true; \
			fi; \
		done; \
	fi

ergo-check: ## Check/install Ergo proxy
	@if ! command -v ergo &> /dev/null; then \
		echo "❌ Ergo is not installed. Installing..."; \
		if command -v brew &> /dev/null; then \
			brew install ergo; \
		else \
			echo "❌ Homebrew not found. Please install Ergo manually:"; \
			echo "   https://github.com/ergo-services/ergo/releases"; \
			exit 1; \
		fi; \
	else \
		echo "✅ Ergo is already installed"; \
	fi

docker-check: ## Check Docker status
	@if ! docker info &> /dev/null; then \
		echo "❌ Docker is not running. Please start Docker and try again."; \
		exit 1; \
	else \
		echo "✅ Docker is running"; \
	fi

quick-start: ergo-check docker-check ## Quick setup with prerequisites check
	@echo "🚀 Quick Start for DeliveryPlus Development"
	@echo "=========================================="
	@echo "✅ Prerequisites check passed"
	@echo ""
	@echo "📦 Deploying development environment..."
	@$(MAKE) local-start
	@echo ""
	@echo "🎉 Setup Complete!"
	@echo "=================="
	@echo ""
	@echo "🌐 Access your application:"
	@echo "   Delivery App:  http://deliveryplus.local (port 3000)"
	@echo "   Management App: http://mgmt.local (port 3001)"
	@echo "   Admin:         http://admin.local"
	@echo ""
	@echo "📊 Check status: make docker-logs"
	@echo "📊 View Ergo logs: make ergo-logs"
	@echo "🛑 Stop Ergo:   make ergo-stop"
	@echo "❌ Stop all:    make docker-stop"

# =============================================================================
# Production Commands
# =============================================================================

prod: ## Start production environment
	@$(MAKE) docker-stop
	@$(MAKE) react-config=nginx.conf.production
	@$(MAKE) docker-start
	@echo "✅ Production environment deployed!"
	@echo "🌐 Access your application at: http://localhost"
	@echo "🔧 Admin interface: http://localhost/admin/"
	@echo "📊 Management API: http://localhost/mgmt/"
	@echo "📱 Delivery app: http://localhost/delivery/"
	@echo "💼 Management app: http://localhost/management/"

# =============================================================================
# Utility Commands
# =============================================================================

docker-logs: ## View Docker logs (area=web, follow=true)
	@if [ "$(area)" = "web" ]; then \
		docker compose logs $(FOLLOW_PARAM) web; \
	elif [ "$(area)" = "frontend" ]; then \
		docker compose logs $(FOLLOW_PARAM) frontend; \
	elif [ "$(area)" = "nginx" ]; then \
		docker compose logs $(FOLLOW_PARAM) nginx; \
	else \
		docker compose logs $(FOLLOW_PARAM); \
	fi

ergo-logs: ## View Ergo logs (follow=true)
	@if [ "$(follow)" = "true" ]; then \
		tail -f ergo.log; \
	else \
		cat ergo.log; \
	fi

nuke-it: ## Clean up all Docker resources
	@echo "🧹 Cleaning up all Docker resources..."
	@docker compose down --volumes --remove-orphans
	@docker system prune -f
	@echo "✅ Cleanup complete!"
