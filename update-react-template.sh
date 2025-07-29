#!/bin/bash

# Update Django template with React build files
echo "Updating Django template with React build files..."

# Check if the React build directory exists
if [ ! -d "apps/staticfiles/react/assets" ]; then
    echo "❌ Error: React build directory not found. Run 'npm run build' in frontend/ first."
    exit 1
fi

# Get the JS and CSS file names from the React build
JS_FILE=$(ls apps/staticfiles/react/assets/index-*.js 2>/dev/null | head -1 | xargs basename)
CSS_FILE=$(ls apps/staticfiles/react/assets/index-*.css 2>/dev/null | head -1 | xargs basename)

# Validate that we found the files
if [ -z "$JS_FILE" ]; then
    echo "❌ Error: No JavaScript file found in apps/staticfiles/react/assets/"
    exit 1
fi

if [ -z "$CSS_FILE" ]; then
    echo "❌ Error: No CSS file found in apps/staticfiles/react/assets/"
    exit 1
fi

echo "✅ Found JS file: $JS_FILE"
echo "✅ Found CSS file: $CSS_FILE"

# Create backup of current template
cp apps/config/templates/react/index.html apps/config/templates/react/index.html.backup 2>/dev/null

# Update the Django template
cat > apps/config/templates/react/index.html << EOF
{% load static %}
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="{% static 'react/vite.svg' %}" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>packageparcels</title>
    <script type="module" crossorigin src="{% static 'react/assets/$JS_FILE' %}"></script>
    <link rel="stylesheet" crossorigin href="{% static 'react/assets/$CSS_FILE' %}">
  </head>
  <body>
    <div id="root"></div>
  </body>
</html>
EOF

echo "✅ Django template updated successfully!"
echo "📝 Backup saved as apps/config/templates/react/index.html.backup" 