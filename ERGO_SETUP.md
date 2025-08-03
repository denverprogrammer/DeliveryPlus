# 🚀 Ergo + Nginx Development Setup

This guide explains how to use Ergo Proxy with custom local domains for a better development experience.

## 🎯 Overview

Instead of using paths like `/admin/`, `/mgmt/`, etc., you can now access each component on its own domain:

| Component | Custom Domain | Port | Purpose |
|-----------|---------------|------|---------|
| Delivery App | `http://deliveryplus.local` | 3000 | Public tracking and delivery |
| Management App | `http://mgmt.local` | 3001 | Admin interface |
| Admin | `http://admin.local` | 80 | Django admin |
| API | `http://api.local` | 80 | Django API |

## 🛠️ Setup

### 1. Install Ergo (if not already installed)
```bash
# macOS
brew install ergo

# Linux
# Download from https://github.com/ergo-services/ergo/releases
```

### 2. Deploy with Custom Domains
```bash
# Deploy development environment with custom domains
make dev

# Or manually start Ergo
ergo run --all
```

### 3. Access Your Application
Once deployed, you can access:

**Primary Access (Recommended):**
- **Delivery App**: http://localhost:3000/
- **Management App**: http://localhost:3001/
- **Admin**: http://localhost/admin/
- **API**: http://localhost/api/

**Custom Domains (if Ergo DNS resolution works):**
- **Delivery App**: http://deliveryplus.local
- **Management App**: http://mgmt.local
- **Admin**: http://admin.local
- **API**: http://api.local

**Note**: Localhost access works immediately. Custom domains require Ergo DNS resolution to be working.

## 🔧 Configuration Files

### Ergo Configuration (`.ergo`)
```
deliveryplus = "http://localhost:3000"
mgmt = "http://localhost:3001"
admin = "http://localhost"
api = "http://localhost"
```

### Nginx Configuration (`nginx.conf`)
- **Multiple server blocks** for each domain
- **Domain-specific routing** to separate frontend apps
- **Static file optimization** for each domain
- **Security headers** for all domains

## 🚀 Deployment Commands

```bash
# Deploy development with custom domains
make dev

# Quick setup with prerequisites check
make quick-start

# Deploy production (standard paths)
make prod

# Check development status
make status-dev

# Stop Ergo proxy
make stop-ergo

# Show help
make help
```

## 🔍 How It Works

### 1. Request Flow
```
Browser → Ergo Proxy (Port 2000) → Nginx (Port 80) → Frontend Container (Ports 3000/3001) + Django
```

### 2. Domain Resolution
```
deliveryplus.local → Ergo → localhost:3000 → Frontend Container (Delivery App)
mgmt.local → Ergo → localhost:3001 → Frontend Container (Management App)
admin.local → Ergo → localhost:80 → nginx → Django Admin
api.local → Ergo → localhost:80 → nginx → Django API
```

### 3. Single Container Architecture
Both frontend apps run in a single container using `concurrently`:
```bash
# Inside the frontend container
npm run dev  # Runs both apps on different ports
```

### 4. Nginx Server Blocks
Each domain has its own server block:
```nginx
server {
    listen 80;
    server_name deliveryplus.local;
    
    location / {
        proxy_pass http://frontend:3000;
        # ... headers and settings
    }
}

server {
    listen 80;
    server_name mgmt.local;
    
    location / {
        proxy_pass http://frontend:3001;
        # ... headers and settings
    }
}
```

## 🎯 Benefits

### ✅ **Clean URLs**
- No more `/admin/` paths
- Each component has its own domain
- Better for development and testing

### ✅ **Isolated Components**
- Delivery app completely separate from management
- API endpoints on their own domain
- Frontend apps isolated

### ✅ **Better Development Experience**
- Clear separation of concerns
- Easier to test individual components
- More realistic production-like setup

### ✅ **Split Frontend Architecture**
- Delivery app for public tracking
- Management app for admin interface
- Shared codebase in `frontend/shared/`
- Single container efficiency

### ✅ **Single Container Benefits**
- **Efficiency**: One container instead of two
- **Resource sharing**: Shared node_modules and dependencies
- **Simpler orchestration**: Single service to manage
- **Consistent environment**: Both apps run in identical conditions

## 🔧 Customization

### Adding New Domains

1. **Update Ergo config** (`.ergo`):
```
newcomponent = "http://localhost:3002"
```

2. **Add Nginx server block** (`nginx.conf`):
```nginx
server {
    listen 80;
    server_name dev.newcomponent.test;
    
    location / {
        proxy_pass http://frontend:3002;
        # ... headers and settings
    }
}
```

3. **Add to frontend container** (`docker-compose.yml`):
```yaml
frontend:
    ports:
        - "3002:3002"  # Add new port
```

### Changing Ports

Edit `docker-compose.yml`:
```yaml
frontend:
    ports:
        - "4000:3000"  # Change delivery port
        - "4001:3001"  # Change management port
```

### Using Different Domains

Edit `nginx.conf`:
```nginx
server {
    listen 80;
    server_name newdomain.local;
    # ... configuration
}
```

## 🐛 Troubleshooting

### Ergo Not Starting
```bash
# Check if port 2000 is available
lsof -i :2000

# Kill existing process
kill $(lsof -t -i:2000)

# Restart Ergo
make dev
```

### Domains Not Resolving
```bash
# Check Ergo status
make status-dev

# Restart Ergo
make stop-ergo
make dev
```

### Frontend Apps Not Starting
```bash
# Check if ports are available
lsof -i :3000
lsof -i :3001

# Restart all services
make destroy
make dev
```

### Nginx Configuration Issues
```bash
# Check nginx config
docker compose exec nginx nginx -t

# View nginx logs
make logs
```

### Docker Issues
```bash
# Restart all services
make destroy
make dev

# Check container status
make status-dev
```

## 🔄 Development Workflow

### 1. Start Development
```bash
make dev
```

### 2. Access Components
- Open http://deliveryplus.local for delivery app
- Open http://mgmt.local for management app
- Open http://admin.local for Django admin
- Open http://api.local for API

### 3. Make Changes
- Edit code in `apps/` or `frontend/`
- Changes are reflected immediately
- No need to restart for most changes

### 4. Stop Development
```bash
# Stop Ergo proxy
make ergo-stop

# Stop all services
make destroy
```

## 📊 Monitoring

### Check Status
```bash
make status-dev
```

### View Logs
```bash
# All services
make logs

# Follow logs
make logs-follow

# Specific service
docker compose logs frontend
```

### Health Checks
```bash
# Delivery app
curl http://deliveryplus.local/health/

# Management app
curl http://mgmt.local/health/
```

## 🚀 Production Deployment

For production, use the standard nginx configuration:

```bash
./deploy.sh prod
```

This uses:
- Standard paths (`/admin/`, `/mgmt/`, etc.)
- Production nginx config (`nginx.conf.production`)
- No Ergo proxy
- Security optimizations

## 📚 Additional Resources

- [Ergo Documentation](https://github.com/ergo-services/ergo)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Django Deployment](https://docs.djangoproject.com/en/5.2/howto/deployment/)

---

**🎯 Key Benefits:**
- ✅ Clean, separate domains for each component
- ✅ Split frontend architecture (delivery + management)
- ✅ Single container efficiency
- ✅ Better development experience
- ✅ Easy switching between dev/prod
- ✅ Isolated component testing
- ✅ Production-like URL structure
- ✅ Flexible deployment options 