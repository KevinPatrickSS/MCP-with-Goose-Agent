FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including curl for health checks
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    curl \
    git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies
RUN pip install --no-cache-dir \
    flask \
    uvicorn \
    fastapi \
    python-dotenv

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p __pycache__ /root/.config/goose

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Expose ports
# 8080 - MCP HTTP Server
# 8501 - Streamlit UI
# 8000 - FastAPI/REST API (if needed)
EXPOSE 8080 8501 8000

# Default command - can be overridden in docker-compose
CMD ["python", "main_goose.py"]