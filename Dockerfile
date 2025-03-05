# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    FLASK_APP=server.py

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for Pillow
RUN apt-get update && apt-get install -y \
    libfreetype6-dev \
    libjpeg-dev \
    locales \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configure locale
RUN sed -i '/fr_FR.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen

# Copy the requirements first (create this file)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container
COPY . .

# Create a non-root user and switch to it for security
RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && chown -R appuser:appuser /app
USER appuser

# Expose the port the app runs on
EXPOSE 5000

# Add health check - use getMealList endpoint which should be lightweight
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/getMealList || exit 1

# Command to run the application with Gunicorn
# Formula for workers: (2 x $num_cores) + 1
# Using 4 as a reasonable default for small to medium workloads
CMD ["gunicorn", "--workers=4", "--threads=2", "--timeout=60", "--keep-alive=5", "--bind=0.0.0.0:5000", "--access-logfile=-", "--error-logfile=-", "server:app"]

