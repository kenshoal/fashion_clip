"""
Hugging Face Spaces entry point
"""
import sys
import logging

# Setup basic logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from main import app
    logger.info("✅ Successfully imported app from main")
except Exception as e:
    logger.error(f"❌ Failed to import app: {e}", exc_info=True)
    # Create minimal app so Space doesn't crash
    from fastapi import FastAPI
    app = FastAPI(title="Error: Failed to load FashionCLIP API")
    
    @app.get("/")
    async def error():
        return {"error": f"Failed to load application: {str(e)}"}

# HF Spaces Docker looks for 'app' variable in app.py
__all__ = ['app']

