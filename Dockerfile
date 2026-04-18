# Use official python slim image
FROM python:3.11-slim

# Install system dependencies needed for compiling C++ extension
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirement files first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install pybind11

# Copy the rest of the project
COPY . .

# Build the C++ extension
RUN pip install -e .

# Expose the port for the API
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
