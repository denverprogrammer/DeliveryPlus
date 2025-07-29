#!/bin/bash

# Build React app
echo "Building React app..."
cd frontend
npm run build

# Copy built files to Django static directory
echo "Copying React build to Django static files..."
mkdir -p ../apps/staticfiles/react
# The build is already in the correct location, no need to copy

echo "React build complete!" 