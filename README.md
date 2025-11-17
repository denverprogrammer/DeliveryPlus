# 🚀 DeliveryPlus

A modern package tracking application with Django backend, React frontend, and comprehensive admin interface.

## 🎯 Features

- **Django Backend**: Admin interface, API endpoints, database management
- **React Frontend**: Modern, responsive user interface
- **Custom Domains**: Development setup with Ergo proxy for clean URLs
- **Production Ready**: Docker-based deployment with nginx
- **AWS Integration**: Elastic Beanstalk deployment support
- **GPS Tracking**: Token-based tracking with GPS coordinates and IP address
- **Notification System**: Automated notifications for tracking events

## 🚀 Quick Start

### Development with Custom Domains
```bash
# One-command setup with prerequisites check
make quick-start

# Or manual setup
make local-start
```

### Standard Development
```bash
# Start standard development environment
make docker-start
```

### Production
```bash
# Start production environment
make prod
```

## 🌐 Access Points

### Development (Custom Domains)
- **Main App**: http://deliveryplus.local
- **Admin**: http://admin.local
- **Management**: http://mgmt.local
- **Tracking**: http://tracking.local

### Production
- **Main App**: http://localhost
- **Admin**: http://localhost/admin/
- **Management**: http://localhost/mgmt/
- **Tracking**: http://localhost/tracking/

## 📋 Available Commands

```bash
# Development
make local-start    # Start with custom domains
make local-stop     # Stop development environment
make quick-start    # Quick setup with checks
make react-build    # Build React app only
make docker-start   # Start Docker containers only
make docker-stop    # Stop Docker containers only

# Ergo Proxy
make ergo-start     # Start Ergo proxy only
make ergo-stop      # Stop Ergo proxy only
make ergo-check     # Check/install Ergo proxy

# Production
make prod           # Production environment
make docker-stop    # Stop all containers

# AWS Deployment
make init           # Initialize EB CLI
make create         # Create EB environment
make deploy         # Deploy to EB
make status         # Check EB status

# Utilities
make help           # Show all commands
make docker-logs    # View Docker logs (area=web, follow=true)
make ergo-logs      # View Ergo logs (follow=true)
make nuke-it        # Clean up all Docker resources
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
- `deliveryplus.local` - Main React application
- `admin.local` - Django admin interface
- `mgmt.local` - Management API endpoints
- `tracking.local` - Tracking API endpoints

## 🔧 Configuration

### Development
- **Ergo Proxy**: Custom domain resolution (.local domains)
- **Nginx**: Domain-specific routing
- **Docker Compose**: Local development environment
- **React Build**: Automatic build on `make local-start`

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
1. **Start Development**: `make local-start` (automatically builds React)
2. **Make Changes**: Edit code in `apps/` or `frontend/`
3. **Rebuild React**: `make react-build` (if frontend changes)
4. **View Changes**: Changes reflect immediately
5. **Check Status**: `make docker-logs`
6. **Stop Development**: `make local-stop`

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
make docker-logs
```

### Logs
```bash
make docker-logs follow=true
```

### Health Check
```bash
# Development
curl http://deliveryplus.local/health/

# Production
curl http://localhost/health/
```

## 🔧 Troubleshooting

### Common Issues
- **Ergo not starting**: Check port 2000 availability
- **Domains not resolving**: Restart with `make local-start`
- **Docker issues**: Clean up with `make nuke-it`
- **React build issues**: Run `make react-build` manually

### Cleanup
```bash
# Stop everything
make local-stop

# Clean all Docker resources
make nuke-it
```

## 🎯 Key Benefits
- ✅ Clean development domains (.local)
- ✅ Production-ready deployment
- ✅ AWS integration
- ✅ Modern React frontend
- ✅ Comprehensive admin interface
- ✅ Easy development workflow
- ✅ Automatic React builds
- ✅ GPS tracking capabilities
- ✅ Notification system

https://mapsplatform.google.com/pricing/