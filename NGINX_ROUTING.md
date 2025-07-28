# 🚀 Nginx Routing Configuration for DeliveryPlus

This document explains how nginx routes different URLs in your DeliveryPlus application.

## 📋 URL Structure

| Domain | Purpose | Backend | Description |
|--------|---------|---------|-------------|
| `dev.deliveryplus.test` | React Frontend | Django | Main React application |
| `dev.admin.test` | Django Admin | Django | Admin interface |
| `dev.mgmt.test` | Management API | Django | Management endpoints |
| `dev.tracking.test` | Tracking API | Django | Tracking endpoints |
| `dev.api.test` | REST API | Django | General API endpoints |
| `/static/` | Static Files | Nginx | React build files |
| `/media/` | Media Files | Nginx | Uploaded media |
| `/health/` | Health Check | Nginx | Health endpoint |

## 🔧 Configuration Files

### Development Configuration
- **File**: `nginx.conf`
- **Purpose**: Development environment with debugging
- **Features**: 
  - Debug toolbar enabled
  - Less restrictive security
  - Development-friendly timeouts

### Production Configuration
- **File**: `nginx.conf.production`
- **Purpose**: Production environment with security
- **Features**:
  - Rate limiting
  - Security headers
  - Gzip compression
  - Cache optimization
  - Hidden file protection

## 🚀 Deployment

### Quick Start
```bash
# Development deployment
./deploy.sh dev

# Production deployment
./deploy.sh prod

# Check status
./deploy.sh status
```

### Manual Deployment
```bash
# Development
docker compose down
docker compose up --build -d

# Production
docker compose -f docker-compose.deploy.yml down
docker compose -f docker-compose.deploy.yml up --build -d
```

## 🔍 How It Works

### 1. URL Routing Logic
```
Request → Nginx → Django → Response
```

### 2. Static File Handling
```
/static/ → Nginx serves directly (faster)
/ → Try static files first, then Django
```

### 3. API Routing
```
/admin/ → Django admin interface
/mgmt/ → Django management views
/tracking/ → Django tracking views
/api/ → Django REST API
```

### 4. React App Routing
```
dev.deliveryplus.test → Django serves React app
dev.deliveryplus.test/any-other-path → Django serves React app (SPA routing)
```

## 🛡️ Security Features

### Production Security
- **Rate Limiting**: Prevents abuse
- **Security Headers**: XSS protection, content type sniffing
- **Hidden Files**: Blocks access to `.` files
- **Server Headers**: Hides server information
- **CSP**: Content Security Policy

### Development Features
- **Debug Toolbar**: Django debug toolbar enabled
- **Relaxed Security**: Easier debugging
- **Verbose Logging**: More detailed logs

## 📊 Performance Optimizations

### Static Files
- **Gzip Compression**: Reduces file sizes
- **Cache Headers**: Long-term caching
- **Direct Serving**: Nginx serves static files

### API Endpoints
- **Connection Pooling**: Reuses connections
- **Timeout Optimization**: Appropriate timeouts
- **Load Balancing**: Ready for multiple servers

## 🔧 Customization

### Adding New Domains

1. **Update Ergo config** (`ergo.toml`):
```toml
[[proxy]]
name = "dev.newcomponent.test"
port = 80
host = "127.0.0.1"
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
Edit `docker-compose.yml`:
```yaml
nginx:
  ports:
    - "8080:80"  # Change 80 to desired port
```

### Domain Configuration
Edit nginx config:
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain
    # ... rest of config
}
```

## 🐛 Troubleshooting

### Common Issues

1. **Static files not loading**
   ```bash
   # Rebuild React app
   cd frontend && npm run build
   # Restart containers
   docker-compose restart
   ```

2. **Admin not accessible**
   ```bash
   # Check Django logs
   docker-compose logs web
   # Check nginx logs
   docker-compose logs nginx
   ```

3. **API endpoints failing**
   ```bash
   # Check Django URL configuration
   python manage.py show_urls
   # Test endpoints directly
   curl http://dev.api.test/
   ```

### Debug Commands
```bash
# Check nginx configuration
docker compose exec nginx nginx -t

# View nginx logs
docker compose logs nginx

# View Django logs
docker compose logs web

# Test nginx config
docker compose exec nginx nginx -s reload
```

## 📈 Monitoring

### Health Check
```bash
# Development
curl http://dev.deliveryplus.test/health/

# Production
curl http://localhost/health/
```

### Performance Monitoring
```bash
# Check response times
curl -w "@curl-format.txt" http://localhost/

# Monitor nginx access logs
docker compose exec nginx tail -f /var/log/nginx/access.log
```

## 🔄 Updates

### Updating Configuration
1. Edit nginx config files
2. Restart nginx container:
   ```bash
   docker compose restart nginx
   ```

### Updating Application
1. Update code
2. Rebuild containers:
   ```bash
   docker compose up --build -d
   ```

## 📚 Additional Resources

- [Nginx Documentation](https://nginx.org/en/docs/)
- [Django Deployment](https://docs.djangoproject.com/en/5.2/howto/deployment/)
- [Docker Compose](https://docs.docker.com/compose/)
- [React Deployment](https://create-react-app.dev/docs/deployment/)

---

**🎯 Key Benefits:**
- ✅ Separate routing for different components
- ✅ Optimized static file serving
- ✅ Security headers and rate limiting
- ✅ Easy development/production switching
- ✅ Health monitoring
- ✅ Scalable architecture 