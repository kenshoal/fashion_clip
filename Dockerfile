FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (minimal to save memory)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements
COPY requirements.txt .

# Install Python dependencies (no cache to save space)
RUN pip install --no-cache-dir --no-compile -r requirements.txt && \
    pip cache purge

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data uploads logs

# Expose port - Render dynamically assigns PORT
# Must use PORT env var, no default (Render requires this)
EXPOSE 10000

# Run the application
# Render provides PORT env var automatically - must use it
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port $PORT --proxy-headers"]

