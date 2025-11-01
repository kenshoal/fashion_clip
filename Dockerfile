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

# Expose port
EXPOSE 7860

# Run the application
# For PythonAnywhere, use uvicorn manually in console
# For other platforms, PORT env var will be provided
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-7860}"]

