# 🚀 Nginx Routing Configuration for DeliveryPlus

This document explains how nginx routes different URLs in your DeliveryPlus application.

## 📋 URL Structure

| Domain | Purpose | Backend | Port | Description |
|--------|---------|---------|------|-------------|
| `deliveryplus.local` | Delivery App | React | 3000 | Public tracking and delivery |
| `mgmt.local` | Management App | React | 3001 | Admin interface |
| `admin.local` | Django Admin | Django | 80 | Django admin interface |
| `/api/` | REST API | Django | 80 | General API endpoints |
| `/static/` | Static Files | Nginx | 80 | React build files |
| `/media/` | Media Files | Nginx | 80 | Uploaded media |
| `/health/` | Health Check | Nginx | 80 | Health endpoint |

## 🔧 Configuration Files

### Development Configuration
- **File**: `nginx.conf`
- **Purpose**: Development environment with debugging
- **Features**: 
  - Debug toolbar enabled
  - Less restrictive security
  - Development-friendly timeouts
  - Split frontend apps (delivery + management)

### Production Configuration
- **File**: `nginx.conf.production`
- **Purpose**: Production environment with security
- **Features**:
  - Rate limiting
  - Security headers
  - Gzip compression
  - Cache optimization
  - Hidden file protection
  - Split frontend apps served as static files

## 🚀 Deployment

### Quick Start
```bash
# Development deployment
make dev

# Production deployment
make prod

# Check status
make status-dev
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
Request → Ergo Proxy → Nginx → Frontend Apps (React) + Django → Response
```

### 2. Static File Handling
```
/static/ → Nginx serves directly (faster)
/delivery/ → Nginx serves delivery app static files
/management/ → Nginx serves management app static files
/ → Try static files first, then Django
```

### 3. API Routing
```
/admin/ → Django admin interface
/mgmt/ → Django management views
/tracking/ → Django tracking views
/api/ → Django REST API
```

### 4. Frontend App Routing
```
deliveryplus.local → Delivery React app (port 3000)
mgmt.local → Management React app (port 3001)
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
- **Hot Reload**: React development servers with hot reload
- **Split Apps**: Separate development servers for delivery and management 