#!/bin/bash

# Update Django template with React build files
echo "Updating Django template with React build files..."

# Get the JS and CSS file names from the React build
JS_FILE=$(ls apps/staticfiles/react/assets/index-*.js | head -1 | xargs basename)
CSS_FILE=$(ls apps/staticfiles/react/assets/index-*.css | head -1 | xargs basename)

echo "Found JS file: $JS_FILE"
echo "Found CSS file: $CSS_FILE"

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

echo "Django template updated successfully!" 