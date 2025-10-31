"""
Initialize FAISS index and migrate existing items
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from supabase import create_client
from services.item_service import ItemService
from config import settings
import httpx
from PIL import Image
import io
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def migrate_existing_items():
    """Migrate existing items from Supabase to FAISS index"""
    
    supabase = create_client(settings.supabase_url, settings.supabase_service_key)
    item_service = ItemService()
    
    logger.info("Fetching all items from Supabase...")
    
    # Get all items with images
    response = supabase.table('clothes').select('*').execute()
    items = response.data
    
    logger.info(f"Found {len(items)} items to process")
    
    processed = 0
    errors = 0
    
    for item in items:
        try:
            item_id = item['id']
            user_id = item['user_id']
            category = item.get('category', 'unknown')
            image_url = item.get('image_url')
            
            if not image_url:
                logger.warning(f"Skipping item {item_id}: no image URL")
                continue
            
            # Download image
            async with httpx.AsyncClient() as client:
                img_response = await client.get(image_url)
                if img_response.status_code != 200:
                    logger.warning(f"Could not download image for item {item_id}")
                    continue
                
                image_data = img_response.content
                image = Image.open(io.BytesIO(image_data)).convert("RGB")
            
            # Process item
            await item_service.process_uploaded_item(
                image_data=image_data,
                item_id=item_id,
                user_id=user_id,
                category=category,
                image_url=image_url,
                name=item.get('name')
            )
            
            processed += 1
            
            if processed % 10 == 0:
                logger.info(f"Processed {processed}/{len(items)} items")
                
        except Exception as e:
            logger.error(f"Error processing item {item.get('id')}: {e}")
            errors += 1
    
    logger.info(f"Migration complete: {processed} processed, {errors} errors")
    logger.info(f"FAISS index now contains {item_service.faiss_manager.get_stats()['total_items']} items")


if __name__ == "__main__":
    asyncio.run(migrate_existing_items())

