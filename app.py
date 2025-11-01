"""
Hugging Face Spaces entry point - Minimal version for debugging
"""
from fastapi import FastAPI

# Create minimal app first to test routing
app = FastAPI(title="FashionCLIP API")

@app.get("/")
async def root():
    return {"status": "ok", "message": "API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Try to import full app
try:
    from main import app as main_app
    # If import succeeds, replace with full app
    app = main_app
except Exception as e:
    # Keep minimal app but add error endpoint
    @app.get("/error")
    async def error_info():
        return {"error": str(e), "type": type(e).__name__}

__all__ = ['app']
