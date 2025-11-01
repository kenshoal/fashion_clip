#!/bin/bash
# Startup script for HF Spaces Docker
set -e

echo "Starting FashionCLIP API..."
echo "PORT=${PORT:-7860}"

# Start uvicorn
exec uvicorn app:app --host 0.0.0.0 --port ${PORT:-7860} --proxy-headers

