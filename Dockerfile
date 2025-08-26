FROM python:3.11-slim

# GitHub Container Registry metadata
LABEL org.opencontainers.image.source=https://github.com/dillpret/bribery

# Explicitly using Python 3.11 for compatibility with gevent
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libc6-dev \
    python3-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files first to leverage Docker caching
COPY requirements.txt requirements-docker.txt ./
# Install dependencies using the Docker-specific requirements file
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copy the rest of the application
COPY . .

# Expose the port Flask runs on
EXPOSE 5000

# Command to run the application
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:5000", "deployment.wsgi:app"]
