# Memory Viewer v2 - Production Docker Image
FROM python:3.11-slim

# Install Node.js for frontend build
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for caching
COPY backend/requirements.txt /app/backend/
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy and build frontend
COPY frontend/package*.json /app/frontend/
RUN cd /app/frontend && npm ci --only=production

COPY frontend/ /app/frontend/
RUN cd /app/frontend && npm run build

# Copy backend
COPY backend/ /app/backend/

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/api/health || exit 1

# Run backend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8501"]
