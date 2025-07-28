#!/bin/sh

pip list

set -e

ls -lac

python manage.py wait_for_db
sleep 10

if [ "$DEBUG" = 1 ]; then
    echo "Making migrations"
    python manage.py makemigrations mgmt
    python manage.py makemigrations tracking
fi

echo "Migrating"
python manage.py migrate --no-input

echo "Loading admin interface theme"
python manage.py loaddata admin_interface_theme_django.json

echo "Building React app"
cd /app/frontend && npm install && npm run build
cd /app

echo "Collecting static files"
python manage.py collectstatic --no-input --clear

# Run migrations in development mode
if [ "$DEBUG" = 1 ]
then
    # Use Django's development server in debug mode with debugger enabled
    # Disable frozen modules to fix debugger warnings
    # python -Xfrozen_modules=off -m debugpy --listen 0.0.0.0:5678 --wait-for-client manage.py runserver 0.0.0.0:8080
    echo "Running development server"
    python manage.py runserver 0.0.0.0:8080
else
    echo "Running production server"
    gunicorn config.asgi:application \
        -w 2 \
        -k uvicorn.workers.UvicornWorker \
        --name gunicorn_worker \
        --workers 3 \
        --timeout 120 \
        --log-level debug \
        --bind 0.0.0.0:8080
fi

exec "$@"
