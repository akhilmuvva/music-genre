# Dockerfile for Django app (music_genre_classifier)
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and project
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy Django project
COPY music_genre_classifier /app/music_genre_classifier
COPY create_dummy_models.py /app/create_dummy_models.py

# Create models dir and generate dummy models if real ones not provided
RUN mkdir -p /app/models && python /app/create_dummy_models.py || true

WORKDIR /app

EXPOSE 8000

# Use gunicorn in production (Procfile also references gunicorn). This keeps
# the Docker image behavior consistent with the Procfile used by PaaS.
CMD ["gunicorn", "music_genre_classifier.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
