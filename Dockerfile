FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy core modules
COPY core/ /app/core/
COPY data/ /app/data/
COPY exercise_counters.py /app/

# Copy addon-specific files
COPY config_manager.py /app/
COPY rtsp_handler.py /app/
COPY mqtt_publisher.py /app/
COPY main.py /app/
COPY model_downloader.py /app/

# Create models directory (models will be downloaded on first run)
RUN mkdir -p /app/models

# Create data directory for Home Assistant options
RUN mkdir -p /data

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the main service
CMD ["python", "-u", "main.py"]
