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
    
    # Use Django's development server in debug mode
    python manage.py runserver 0.0.0.0:8080
else
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
