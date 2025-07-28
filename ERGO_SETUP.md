# 🚀 Ergo + Nginx Development Setup

This guide explains how to use Ergo Proxy with custom local domains for a better development experience.

## 🎯 Overview

Instead of using paths like `/admin/`, `/mgmt/`, etc., you can now access each component on its own domain:

| Component | Custom Domain |
|-----------|---------------|
| Main App | `http://deliveryplus.local` |
| Admin | `http://admin.local` |
| Management | `http://mgmt.local` |
| Tracking | `http://tracking.local` |
| API | `http://api.local` |

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
- **Main App**: http://localhost/
- **Admin**: http://localhost/admin/
- **Management**: http://localhost/mgmt/
- **Tracking**: http://localhost/tracking/
- **API**: http://localhost/api/

**Custom Domains (if Ergo DNS resolution works):**
- **Main App**: http://deliveryplus.local
- **Admin**: http://admin.local
- **Management**: http://mgmt.local
- **Tracking**: http://tracking.local
- **API**: http://api.local

**Note**: Localhost access works immediately. Custom domains require Ergo DNS resolution to be working.

## 🔧 Configuration Files

### Ergo Configuration (`.ergo`)
```
deliveryplus = "http://localhost"
admin = "http://localhost"
mgmt = "http://localhost"
tracking = "http://localhost"
api = "http://localhost"
```

### Nginx Configuration (`nginx.conf.dev`)
- **Multiple server blocks** for each domain
- **Domain-specific routing** to Django paths
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
Browser → Ergo Proxy (Port 2000) → Nginx (Port 80) → Django
```

### 2. Domain Resolution
```
admin.local → Ergo → localhost:80 → nginx → /admin/
mgmt.local → Ergo → localhost:80 → nginx → /mgmt/
tracking.local → Ergo → localhost:80 → nginx → /tracking/
api.local → Ergo → localhost:80 → nginx → /api/
deliveryplus.local → Ergo → localhost:80 → nginx → /
```

### 3. Nginx Server Blocks
Each domain has its own server block:
```nginx
server {
    listen 80;
    server_name dev.admin.test;
    
    location / {
        proxy_pass http://web/admin/;
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
- Admin interface completely separate
- API endpoints on their own domain
- Frontend app isolated

### ✅ **Better Development Experience**
- Clear separation of concerns
- Easier to test individual components
- More realistic production-like setup

### ✅ **Clean Development Experience**
- Each component has its own domain
- No more confusing paths
- Production deployment unchanged

## 🔧 Customization

### Adding New Domains

1. **Update Ergo config** (`.ergo`):
```
newcomponent = "http://localhost"
```

2. **Add Nginx server block** (`nginx.conf.dev`):
```nginx
server {
    listen 80;
    server_name dev.newcomponent.test;
    
    location / {
        proxy_pass http://web/newcomponent/;
        # ... headers and settings
    }
}
```

3. **Add Django URL** (`apps/config/urls.py`):
```python
path("newcomponent/", include("newcomponent.urls")),
```

### Changing Ports

Edit `ergo.toml`:
```toml
[server]
port = 3000  # Change from 2000
```

### Using Different Domains

Edit `ergo.toml`:
```toml
[[proxy]]
name = "admin.localhost"
port = 80
host = "127.0.0.1"
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
- Open http://dev.deliveryplus.test for main app
- Open http://dev.admin.test for admin
- Open http://dev.mgmt.test for management
- Open http://dev.tracking.test for tracking
- Open http://dev.api.test for API

### 3. Make Changes
- Edit code in `apps/` or `frontend/`
- Changes are reflected immediately
- No need to restart for most changes

### 4. Stop Development
```bash
# Stop Ergo proxy
make stop-ergo

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
```

### Health Checks
```bash
# Main app
curl http://dev.deliveryplus.test/health/
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
- ✅ Better development experience
- ✅ Easy switching between dev/prod
- ✅ Isolated component testing
- ✅ Production-like URL structure
- ✅ Flexible deployment options 