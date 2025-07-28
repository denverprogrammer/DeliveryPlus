# 🚀 DeliveryPlus

A modern package tracking application with Django backend, React frontend, and comprehensive admin interface.

## 🎯 Features

- **Django Backend**: Admin interface, API endpoints, database management
- **React Frontend**: Modern, responsive user interface
- **Custom Domains**: Development setup with Ergo proxy for clean URLs
- **Production Ready**: Docker-based deployment with nginx
- **AWS Integration**: Elastic Beanstalk deployment support

## 🚀 Quick Start

### Development with Custom Domains
```bash
# One-command setup with prerequisites check
make quick-start

# Or manual setup
make dev
```

### Standard Development
```bash
# Start standard development environment
make start
```

### Production
```bash
# Start production environment
make prod
```

## 🌐 Access Points

### Development (Custom Domains)
- **Main App**: http://dev.deliveryplus.test
- **Admin**: http://dev.admin.test
- **Management**: http://dev.mgmt.test
- **Tracking**: http://dev.tracking.test
- **API**: http://dev.api.test

### Production
- **Main App**: http://localhost
- **Admin**: http://localhost/admin/
- **Management**: http://localhost/mgmt/
- **Tracking**: http://localhost/tracking/
- **API**: http://localhost/api/

## 📋 Available Commands

```bash
# Development
make dev          # Start with custom domains
make quick-start  # Quick setup with checks
make start        # Standard development
make stop-ergo    # Stop Ergo proxy

# Production
make prod         # Production environment
make destroy      # Stop all containers

# AWS Deployment
make init         # Initialize EB CLI
make create       # Create EB environment
make deploy       # Deploy to EB
make status       # Check EB status

# Utilities
make help         # Show all commands
make status-dev   # Check development status
make logs         # View logs
make logs-follow  # Follow logs
make nuke-it      # Clean up everything
```

## 🏗️ Architecture

### Components
- **Django**: Admin interface, API endpoints, database
- **React**: Frontend application, user interface
- **Nginx**: Reverse proxy, static file serving
- **Ergo**: Development domain resolution
- **Docker**: Containerization and orchestration

### URL Structure (Production)
- `/admin/` - Django admin interface
- `/mgmt/` - Management API endpoints
- `/tracking/` - Tracking API endpoints
- `/api/` - General REST API
- `/` - React frontend application

### Development Domains
- `dev.deliveryplus.test` - Main React application
- `dev.admin.test` - Django admin interface
- `dev.mgmt.test` - Management API endpoints
- `dev.tracking.test` - Tracking API endpoints
- `dev.api.test` - General REST API

## 🔧 Configuration

### Development
- **Ergo Proxy**: Custom domain resolution
- **Nginx**: Domain-specific routing
- **Docker Compose**: Local development environment

### Production
- **Nginx**: Production-optimized configuration
- **Security**: Rate limiting, headers, compression
- **AWS**: Elastic Beanstalk deployment

## 📚 Documentation

- [Ergo Setup Guide](ERGO_SETUP.md) - Custom domain development
- [Nginx Routing Guide](NGINX_ROUTING.md) - URL routing configuration

## 🛠️ Development

### Prerequisites
- Docker & Docker Compose
- Ergo (for custom domains)
- Node.js (for React development)

### Workflow
1. **Start Development**: `make dev`
2. **Make Changes**: Edit code in `apps/` or `frontend/`
3. **View Changes**: Changes reflect immediately
4. **Check Status**: `make status-dev`
5. **Stop Development**: `make destroy`

## 🚀 Deployment

### Local Production
```bash
make prod
```

### AWS Deployment
```bash
make deploy
```

## 📊 Monitoring

### Status Check
```bash
make status-dev
```

### Logs
```bash
make logs-follow
```

### Health Check
```bash
# Development
curl http://dev.deliveryplus.test/health/

# Production
curl http://localhost/health/
```

## 🔧 Troubleshooting

### Common Issues
- **Ergo not starting**: Check port 2000 availability
- **Domains not resolving**: Restart with `make dev`
- **Docker issues**: Clean up with `make nuke-it`

### Cleanup
```bash
# Stop everything
make destroy

# Clean all Docker resources
make nuke-it
```

---

**🎯 Key Benefits:**
- ✅ Clean development domains
- ✅ Production-ready deployment
- ✅ AWS integration
- ✅ Modern React frontend
- ✅ Comprehensive admin interface
- ✅ Easy development workflow
