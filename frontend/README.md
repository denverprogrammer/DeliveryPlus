# React Frontend for DeliveryPlus

This is the React frontend for the DeliveryPlus tracking application. It provides a modern, responsive user interface while keeping the Django admin and API backend intact.

## Features

- **Modern React 18** with TypeScript
- **React Router** for client-side routing
- **React Bootstrap** for UI components
- **Axios** for API communication
- **Vite** for fast development and building

## Pages

- **Home** (`/`) - Landing page
- **Tracking** (`/tracking`) - Package tracking interface
- **Redirect** (`/redirects`) - Package redirect interface
- **Login** (`/login`) - Authentication
- **Dashboard** (`/dashboard`) - Management dashboard
- **Agents** (`/agents`) - Agent management
- **Agent Form** (`/agents/add`, `/agents/:id/edit`) - Create/edit agents
- **Company Edit** (`/company/edit`) - Company settings

## Development

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start development server:
   ```bash
   npm run dev
   ```

The development server will run on `http://localhost:5173` with proxy configuration to forward API calls to the Django backend at `http://localhost:8000`.

### Building for Production

1. Build the React app:
   ```bash
   npm run build
   ```

2. The built files will be output to `../apps/staticfiles/react/` and served by Django.

## API Integration

The React app communicates with the Django backend through REST API endpoints:

- **Tracking**: `/tracking/` and `/tracking/:token/`
- **Redirects**: `/tracking/redirects/` and `/tracking/redirects/:token/`
- **Management**: `/mgmt/` endpoints for agents, company, etc.

## Architecture

- **Django Backend**: Handles admin interface, API endpoints, and serves the React app
- **React Frontend**: Handles user-facing pages and interactions
- **Static Files**: React build is served through Django's static file system

## Development Workflow

1. **Frontend Development**: Work in the `frontend/` directory
2. **Backend Development**: Work in the `apps/` directory
3. **API Development**: Add new endpoints in Django and update React API service
4. **Deployment**: Build React and let Django serve the static files

## Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
```

## Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Notes

- The Django admin interface remains unchanged and accessible at `/admin/`
- API endpoints are available at `/api/` and `/mgmt/`
- React routes are handled by Django's catch-all route
- Static files are collected and served by Django
