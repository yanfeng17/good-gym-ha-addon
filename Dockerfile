FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY homeassistant/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy core modules from parent project
COPY core/ /app/core/
COPY data/ /app/data/
COPY models/ /app/models/
COPY exercise_counters.py /app/

# Copy addon-specific files
COPY homeassistant/*.py /app/

RUN mkdir -p /data

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the main service
CMD ["python", "-u", "main.py"]
