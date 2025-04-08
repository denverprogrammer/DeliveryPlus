# Dockerfile.web

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    netcat gcc postgresql-client libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install --upgrade pip && pip install poetry && poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

# Copy application code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port 8080 (important!)
EXPOSE 8080

# Start Gunicorn server on port 8080
# CMD ["gunicorn", "deliveryplus.wsgi:application", "--bind", "0.0.0.0:8080"]
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]
# ENTRYPOINT ["tail", "-f", "/dev/null"]