# Frontend Split Architecture

This frontend has been split into two separate sites with a shared codebase, running in a single container:

## Folder Structure

```
frontend/
├── delivery/           # Delivery site (public tracking)
│   ├── DeliveryApp.tsx
│   ├── main.tsx
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── management/         # Management site (admin interface)
│   ├── ManagementApp.tsx
│   ├── main.tsx
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── shared/            # Shared code between sites
│   ├── components/
│   │   └── Navigation.tsx
│   ├── services/
│   │   ├── api.ts
│   │   └── trackingUtils.ts
│   └── pages/
│       ├── Home.tsx
│       ├── Tracking.tsx
│       └── Redirect.tsx
└── package.json       # Root package with combined scripts
```

## 1. Delivery Site
- **Purpose**: Public-facing tracking and delivery functionality
- **Location**: `frontend/delivery/`
- **Routes**: `/`, `/tracking`, `/redirects`
- **Build Output**: `apps/staticfiles/delivery/`
- **Development Port**: 3000
- **Development**: `npm run dev:delivery`
- **Build**: `npm run build:delivery`

## 2. Management Site
- **Purpose**: Administrative interface for managing recipients and companies
- **Location**: `frontend/management/`
- **Routes**: `/login`, `/dashboard`, `/recipients`, `/company/edit`
- **Build Output**: `apps/staticfiles/management/`
- **Development Port**: 3001
- **Development**: `npm run dev:management`
- **Build**: `npm run build:management`

## Development

### Initial Setup
```bash
# Install dependencies for all apps
npm run install:all
```

### Running Both Sites Together (Recommended)
```bash
# Run both delivery and management sites concurrently
npm run dev
```
This will start:
- **Delivery app** on http://localhost:3000
- **Management app** on http://localhost:3001

### Running Individual Sites
```bash
# Delivery site only
npm run dev:delivery

# Management site only
npm run dev:management
```

### Building Individual Sites
```bash
# Build delivery site
npm run build:delivery

# Build management site
npm run build:management

# Build both sites
npm run build:all
```

### Working in Individual Apps
```bash
# Work in delivery app
cd delivery
npm run dev

# Work in management app
cd management
npm run dev
```

## Docker Integration

The `entrypoint.sh` script automatically handles:
- Installing dependencies for all apps
- Running both development servers concurrently in a single container
- Building both apps in production mode

### Docker Commands
```bash
# Development mode - runs both apps on ports 3000 and 3001 in single container
docker-compose up --build -d

# Production mode - builds both apps
NODE_ENV=production docker-compose up --build -d
```

### Single Container Benefits
- **Efficiency**: One container instead of two
- **Resource sharing**: Shared node_modules and dependencies
- **Simpler orchestration**: Single service to manage
- **Consistent environment**: Both apps run in identical conditions
