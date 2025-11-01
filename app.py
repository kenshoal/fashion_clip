"""
Hugging Face Spaces entry point
This file is used by Hugging Face Spaces to run the FastAPI application
"""
import os
import sys

# Hugging Face Spaces automatically makes secrets available as environment variables
# No need to manually set them here

# Import the FastAPI app from main
from main import app

# Hugging Face Spaces will automatically detect the 'app' variable
# For Docker deployment, use: uvicorn app:app --host 0.0.0.0 --port ${PORT:-7860}
# For Python SDK, HF Spaces handles this automatically
__all__ = ['app']

