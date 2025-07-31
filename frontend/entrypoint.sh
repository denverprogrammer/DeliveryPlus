#!/bin/sh

# Node.js container entrypoint script
# Handles both build and development modes

npm list

set -e

ls -lac


echo "🔧 Node.js container starting..."
echo "📦 NODE_ENV: ${NODE_ENV}"



# Install dependencies only in development
if [ "$NODE_ENV" = "development" ]; then
    echo "📥 Installing dependencies..."
    # Run npm install as root to avoid permission issues
    npm run dev
else
    npm run build
fi
