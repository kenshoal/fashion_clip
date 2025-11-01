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

# Expose port (Render uses 10000, HF Spaces uses 7860)
EXPOSE 10000

# Run the application
# PORT env var is provided by platform (Render=10000, HF Spaces=7860)
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-10000} --proxy-headers"]

