# Production Dockerfile for Stock Market Big Data Analytics Platform
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=3000

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency specifications and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Run preprocessing & local MapReduce pipeline during image build to pre-populate outputs
RUN python run.py generate && \
    python run.py preprocess && \
    python run.py mapreduce-local && \
    python run.py analytics

# Expose production port
EXPOSE 3000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:3000/api/overview || exit 1

# Launch production server via Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:3000", "--workers", "3", "--timeout", "120", "wsgi:app"]
