"""
FastAPI application for FashionCLIP outfit recommendations
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import logging
from pathlib import Path

from config import settings
from services.item_service import ItemService

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="FashionCLIP Outfit Recommendation API",
    description="AI-powered outfit recommendations using FashionCLIP embeddings",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
item_service = ItemService()


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


# Health check
@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    try:
        stats = item_service.get_stats()
        return {
            "status": "healthy",
            "service": "fashion-clip-api",
            "version": "1.0.0",
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


# Upload and process item
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
        result = await item_service.process_uploaded_item(
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


# Get recommendations for an item
@app.post("/api/v1/items/recommendations")
async def get_item_recommendations(request: RecommendationRequest):
    """
    Get recommendations for a specific item
    
    Returns items from user's wardrobe that match stylistically
    """
    try:
        recommendations = await item_service.get_recommendations(
            item_id=request.item_id,
            user_id=request.user_id,
            k=request.k,
            target_categories=request.target_categories,
            min_similarity=request.min_similarity
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


# Get outfit recommendations
@app.post("/api/v1/outfits/recommend")
async def get_outfit_recommendations(request: OutfitRecommendationRequest):
    """
    Get complete outfit recommendations based on multiple items
    
    Returns recommendations organized by category
    """
    try:
        recommendations = await item_service.get_outfit_recommendations(
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


# Remove item from index
@app.delete("/api/v1/items/{item_id}")
async def remove_item(item_id: str):
    """
    Remove item from FAISS index
    """
    try:
        success = await item_service.remove_item(item_id)
        
        if success:
            return {"success": True, "message": f"Item {item_id} removed from index"}
        else:
            raise HTTPException(status_code=404, detail=f"Item {item_id} not found in index")
            
    except Exception as e:
        logger.error(f"Error removing item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Get stats
@app.get("/api/v1/stats")
async def get_stats():
    """Get service statistics"""
    try:
        stats = item_service.get_stats()
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

