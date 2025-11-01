"""
Hugging Face Spaces entry point
"""
import sys
import logging

# Setup logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("=" * 50)
logger.info("Starting FashionCLIP API on Hugging Face Spaces")
logger.info("=" * 50)

# Create minimal working app first
from fastapi import FastAPI
app = FastAPI(title="FashionCLIP API")

@app.get("/")
async def root():
    return {"status": "ok", "message": "API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Try to import full app - with detailed error handling
logger.info("Attempting to import full app from main.py...")
try:
    from main import app as main_app
    logger.info("✅ Successfully imported full app from main.py")
    # Replace with full app
    app = main_app
    logger.info("✅ Using full FashionCLIP API")
except ImportError as e:
    logger.error(f"❌ ImportError: {e}", exc_info=True)
    @app.get("/error")
    async def error_info():
        return {"error": f"Import error: {str(e)}", "type": "ImportError"}
except Exception as e:
    logger.error(f"❌ Error loading full app: {e}", exc_info=True)
    @app.get("/error")
    async def error_info():
        return {"error": str(e), "type": type(e).__name__}

logger.info("Application initialized successfully")
__all__ = ['app']
