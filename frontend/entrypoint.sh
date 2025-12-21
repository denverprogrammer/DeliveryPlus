#!/bin/sh

# Node.js container entrypoint script
# Handles both build and development modes for split frontend apps

npm list

set -e

ls -lac

echo "🔧 Node.js container starting..."
echo "📦 NODE_ENV: ${NODE_ENV}"

# Install dependencies for all apps
echo "📥 Installing dependencies for all apps..."
npm run install:all

# Install dependencies only in development
if [ "$NODE_ENV" = "development" ]; then
    echo "🚀 Starting development servers..."
    echo "📱 Delivery app will be available on port 3000"
    echo "💼 Management app will be available on port 3001"
    echo "📸 Image review app will be available on port 3002"
    # Run all apps concurrently in a single container
    npm run dev
else
    echo "🏗️ Building all apps..."
    npm run build:all
fi
