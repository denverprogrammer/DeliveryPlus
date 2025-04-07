# ✅ Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install dependencies
COPY pyproject.toml poetry.lock /app/
RUN pip install --upgrade pip \
    && pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy project files
COPY ./apps /app/

# Collect static files
RUN mkdir -p /app/staticfiles

# Run application
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]
# ENTRYPOINT ["tail", "-f", "/dev/null"]