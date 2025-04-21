# Dockerfile.web

FROM python:3.11-slim

# Python writes directly to stdout/stderr without buffering
ENV PYTHONUNBUFFERED=1

# Prevent Python from creating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    netcat-openbsd gcc postgresql-client libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install --upgrade pip && pip install poetry && poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# Copy application code
COPY ./apps /app/

# Collect static files
RUN mkdir -p /app/staticfiles && python manage.py collectstatic --noinput

# Expose port 8080 (important!)
EXPOSE 8080

# Start Gunicorn server on port 8080
# CMD ["gunicorn", "packageparcels.wsgi:application", "--bind", "0.0.0.0:8080"]
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]
# ENTRYPOINT ["tail", "-f", "/dev/null"]