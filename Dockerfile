FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system packages required by OpenCV and common image libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY . /app

# Create non-root user and switch
RUN useradd -m appuser || true
USER appuser

EXPOSE 5000

ENV FLASK_ENV=production

# Use gunicorn to serve the Flask app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
