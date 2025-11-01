"""
FastAPI application for FashionCLIP outfit recommendations
"""
import os
import logging
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from config import settings
from services.item_service import ItemService

# Configure logging - ensure logs directory exists
try:
    os.makedirs(os.path.dirname(settings.log_file), exist_ok=True)
except (OSError, TypeError):
    pass  # If log_file is relative or directory doesn't need creation

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app for Hugging Face Spaces
app = FastAPI(
    title="FashionCLIP Outfit Recommendation API",
    description="AI-powered outfit recommendations using FashionCLIP embeddings",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
# For HF Spaces, allow all origins - needed for the Space interface
cors_origins = settings.cors_origins
# If cors_origins is empty or only has localhost, allow all for HF Spaces
if not cors_origins or cors_origins == ["http://localhost:5173"]:
    cors_origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services lazily (delay model loading until first request)
# This prevents slow model download from blocking app startup
item_service = None

def get_item_service():
    """Get or create ItemService instance (lazy initialization)"""
    global item_service
    if item_service is None:
        item_service = ItemService()
    return item_service


# Pydantic models
class RecommendationRequest(BaseModel):
    item_id: str
    user_id: str
    k: int = 10
    target_categories: Optional[List[str]] = None
    min_similarity: float = 0.5


class OutfitRecommendationRequest(BaseModel):
    base_items: List[str]
    user_id: str
    k_per_category: int = 3


class ItemUploadRequest(BaseModel):
    item_id: str
    user_id: str
    category: str
    image_url: Optional[str] = None
    name: Optional[str] = None


# Root endpoint for HF Spaces
@app.get("/")
async def root():
    """Root endpoint - shows API information"""
    return {
        "service": "FashionCLIP Outfit Recommendation API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": ["/health", "/api/v1/health"],
            "stats": ["/stats", "/api/v1/stats"],
            "upload": ["/items/upload", "/api/v1/items/upload"],
            "recommendations": ["/items/recommendations", "/api/v1/items/recommendations"],
            "outfits": ["/outfits/recommend", "/api/v1/outfits/recommend"],
            "docs": "/docs"
        }
    }

# Health check - with both paths for HF Spaces compatibility
@app.get("/health")
@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    try:
        service = get_item_service()
        stats = service.get_stats()
        return {
            "status": "healthy",
            "service": "fashion-clip-api",
            "version": "1.0.0",
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


# Upload and process item - with both paths for HF Spaces compatibility
@app.post("/items/upload")
@app.post("/api/v1/items/upload")
async def upload_item(
    file: UploadFile = File(...),
    item_id: str = None,
    user_id: str = None,
    category: str = None,
    image_url: str = None,
    name: str = None
):
    """
    Upload item image and generate embedding
    
    Expects multipart form data with:
    - file: Image file
    - item_id: Item ID from Supabase
    - user_id: User ID
    - category: Item category
    - image_url: (optional) URL where image is stored
    - name: (optional) Item name
    """
    try:
        # Validate file
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image data
        image_data = await file.read()
        
        # Check file size
        max_size = settings.max_upload_size_mb * 1024 * 1024
        if len(image_data) > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {settings.max_upload_size_mb}MB"
            )
        
        # Validate required fields
        if not all([item_id, user_id, category]):
            raise HTTPException(
                status_code=400,
                detail="Missing required fields: item_id, user_id, category"
            )
        
        # Process item
        service = get_item_service()
        result = await service.process_uploaded_item(
            image_data=image_data,
            item_id=item_id,
            user_id=user_id,
            category=category,
            image_url=image_url,
            name=name
        )
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Get recommendations for an item - with both paths for HF Spaces compatibility
@app.post("/items/recommendations")
@app.post("/api/v1/items/recommendations")
async def get_item_recommendations(
    request: RecommendationRequest,
    image_url: Optional[str] = None
):
    """
    Get recommendations for a specific item
    
    Returns items from user's wardrobe that match stylistically
    
    Note: If Supabase is not configured, image_url query parameter must be provided
    """
    try:
        service = get_item_service()
        recommendations = await service.get_recommendations(
            item_id=request.item_id,
            user_id=request.user_id,
            k=request.k,
            target_categories=request.target_categories,
            min_similarity=request.min_similarity,
            image_url=image_url
        )
        
        return {
            "success": True,
            "item_id": request.item_id,
            "recommendations": recommendations,
            "count": len(recommendations)
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Get outfit recommendations - with both paths for HF Spaces compatibility
@app.post("/outfits/recommend")
@app.post("/api/v1/outfits/recommend")
async def get_outfit_recommendations(request: OutfitRecommendationRequest):
    """
    Get complete outfit recommendations based on multiple items
    
    Returns recommendations organized by category
    """
    try:
        service = get_item_service()
        recommendations = await service.get_outfit_recommendations(
            base_items=request.base_items,
            user_id=request.user_id,
            k_per_category=request.k_per_category
        )
        
        return {
            "success": True,
            "base_items": request.base_items,
            "recommendations": recommendations
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting outfit recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Remove item from index - with both paths for HF Spaces compatibility
@app.delete("/items/{item_id}")
@app.delete("/api/v1/items/{item_id}")
async def remove_item(item_id: str):
    """
    Remove item from FAISS index
    """
    try:
        service = get_item_service()
        success = await service.remove_item(item_id)
        
        if success:
            return {"success": True, "message": f"Item {item_id} removed from index"}
        else:
            raise HTTPException(status_code=404, detail=f"Item {item_id} not found in index")
            
    except Exception as e:
        logger.error(f"Error removing item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Get stats - with both paths for HF Spaces compatibility
@app.get("/stats")
@app.get("/api/v1/stats")
async def get_stats():
    """Get service statistics"""
    try:
        service = get_item_service()
        stats = service.get_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )

