#!/bin/sh

pip list

set -e

ls -lac

python manage.py wait_for_db
sleep 10



# Run migrations in development mode
if [ "$DEBUG" = 1 ]
then
    python manage.py makemigrations mgmt
    python manage.py makemigrations tracking
    python manage.py migrate --no-input
    
    # Use Django's development server in debug mode with debugger enabled
    # Disable frozen modules to fix debugger warnings
    # python -Xfrozen_modules=off -m debugpy --listen 0.0.0.0:5678 --wait-for-client manage.py runserver 0.0.0.0:8080
    python manage.py runserver 0.0.0.0:8080
else
    python manage.py loaddata admin_interface_theme_django.json
    python manage.py loaddata admin_interface_theme_bootstrap.json
    python manage.py loaddata admin_interface_theme_foundation.json
    python manage.py loaddata admin_interface_theme_uswds.json

    # Production mode with Gunicorn
    python manage.py collectstatic --no-input --clear

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
