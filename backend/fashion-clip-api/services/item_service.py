"""
Service for managing clothing items and embeddings
"""
import asyncio
from typing import List, Dict, Optional, TYPE_CHECKING
from pathlib import Path
import logging
from PIL import Image
import io

if TYPE_CHECKING:
    from supabase import Client

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None  # Will be Optional[Client] in type hints

from models.embedding_model import FashionCLIPEmbedder
from models.faiss_manager import FAISSManager
from config import settings

logger = logging.getLogger(__name__)


class ItemService:
    """
    Service for managing clothing items, embeddings, and recommendations
    """
    
    def __init__(self):
        # Initialize Supabase only if credentials are provided and library is available
        self.supabase: Optional[Client] = None
        if not SUPABASE_AVAILABLE:
            logger.warning("Supabase library not installed - running in standalone mode")
        elif settings.supabase_url and settings.supabase_service_key:
            try:
                self.supabase = create_client(
                    settings.supabase_url,
                    settings.supabase_service_key
                )
                logger.info("Supabase client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Supabase: {e}")
        else:
            logger.warning("Supabase credentials not provided - running in standalone mode")
        
        self.embedder = FashionCLIPEmbedder(
            model_name=settings.fashion_clip_model,
            device=settings.device
        )
        self.faiss_manager = FAISSManager(
            index_path=settings.faiss_index_path,
            dimension=settings.faiss_index_dimension
        )
    
    async def process_uploaded_item(
        self,
        image_data: bytes,
        item_id: str,
        user_id: str,
        category: str,
        image_url: Optional[str] = None,
        name: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Process uploaded image, generate embedding, and store in index
        
        Args:
            image_data: Raw image bytes
            item_id: Unique item ID (from Supabase)
            user_id: User ID
            category: Item category (top, bottom, shoes, etc.)
            image_url: URL where image is stored
            name: Item name
            metadata: Additional metadata
            
        Returns:
            Dict with item info and embedding status
        """
        try:
            # Load image
            image = Image.open(io.BytesIO(image_data)).convert("RGB")
            
            # Generate embedding
            logger.info(f"Generating embedding for item {item_id}")
            embedding = self.embedder.get_image_embedding(image)
            
            # Store in FAISS index
            item_metadata = {
                'item_id': item_id,
                'user_id': user_id,
                'category': category,
                'image_url': image_url,
                'name': name or f"{category} item",
                **(metadata or {})
            }
            
            faiss_id = self.faiss_manager.add_item(embedding, item_metadata)
            
            # Optionally: Store embedding in Supabase for backup
            # (FAISS is primary, but DB backup is useful)
            await self._store_embedding_backup(item_id, embedding)
            
            logger.info(f"Successfully processed item {item_id}")
            
            return {
                'success': True,
                'item_id': item_id,
                'faiss_id': faiss_id,
                'embedding_dimension': len(embedding),
                'metadata': item_metadata
            }
            
        except Exception as e:
            logger.error(f"Error processing item {item_id}: {e}")
            raise
    
    async def get_recommendations(
        self,
        item_id: str,
        user_id: str,
        k: int = 10,
        target_categories: Optional[List[str]] = None,
        min_similarity: float = 0.5,
        image_url: Optional[str] = None
    ) -> List[Dict]:
        """
        Get recommendations for an item
        
        Args:
            item_id: Source item ID
            user_id: User ID (only recommend from this user's wardrobe)
            k: Number of recommendations
            target_categories: Categories to recommend (e.g., ['bottom', 'shoes'])
            min_similarity: Minimum similarity score
            image_url: Optional image URL (if Supabase not available)
            
        Returns:
            List of recommended items with similarity scores
        """
        try:
            # If Supabase is available, get item from database
            if self.supabase:
                item_response = self.supabase.table('clothes').select('*').eq('id', item_id).execute()
                
                if not item_response.data:
                    raise ValueError(f"Item {item_id} not found")
                
                item = item_response.data[0]
                image_url = item.get('image_url') or image_url
            else:
                # In standalone mode, image_url must be provided
                if not image_url:
                    raise ValueError(f"Item {item_id} has no image URL and Supabase is not configured")
            
            if not image_url:
                raise ValueError(f"Item {item_id} has no image URL")
            
            # Download image and generate query embedding
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url)
                response.raise_for_status()
                image_data = response.content
            
            image = Image.open(io.BytesIO(image_data)).convert("RGB")
            query_embedding = self.embedder.get_image_embedding(image)
            
            # Search FAISS index
            recommendations = self.faiss_manager.search(
                query_embedding=query_embedding,
                k=k,
                filter_user_id=user_id,
                filter_categories=target_categories,
                exclude_item_id=item_id,
                min_similarity=min_similarity
            )
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommendations for item {item_id}: {e}")
            raise
    
    async def get_outfit_recommendations(
        self,
        base_items: List[str],  # List of item IDs
        user_id: str,
        k_per_category: int = 3
    ) -> Dict[str, List[Dict]]:
        """
        Get complete outfit recommendations based on multiple items
        
        Args:
            base_items: List of item IDs to build outfit from
            user_id: User ID
            k_per_category: Number of recommendations per category
            
        Returns:
            Dict mapping category to list of recommended items
        """
        try:
            # Get all base items (if Supabase is available)
            if self.supabase:
                items_response = self.supabase.table('clothes').select('*').in_('id', base_items).execute()
                items = items_response.data
                
                if not items:
                    raise ValueError("No base items found")
            else:
                # In standalone mode, we need image URLs to be provided via metadata
                # For now, raise error - this endpoint requires Supabase
                raise ValueError("Outfit recommendations require Supabase configuration")
            
            # Get embeddings for base items
            embeddings = []
            for item in items:
                if not item.get('image_url'):
                    continue
                
                import httpx
                async with httpx.AsyncClient() as client:
                    response = await client.get(item['image_url'])
                    if response.status_code == 200:
                        image = Image.open(io.BytesIO(response.content)).convert("RGB")
                        embedding = self.embedder.get_image_embedding(image)
                        embeddings.append(embedding)
            
            if not embeddings:
                raise ValueError("Could not generate embeddings for base items")
            
            # Average embeddings to get "outfit style"
            avg_embedding = sum(embeddings) / len(embeddings)
            # Normalize
            import numpy as np
            avg_embedding = avg_embedding / np.linalg.norm(avg_embedding)
            
            # Determine categories to recommend based on base items
            base_categories = {item['category'] for item in items}
            
            # Category mapping: what to recommend given base categories
            category_map = {
                'top': ['bottom', 'shoes', 'outerwear'],
                'bottom': ['top', 'shoes', 'outerwear'],
                'dress': ['shoes', 'outerwear'],
                'outerwear': ['top', 'bottom', 'shoes']
            }
            
            target_categories = set()
            for cat in base_categories:
                target_categories.update(category_map.get(cat, ['top', 'bottom', 'shoes']))
            
            # Remove categories already in base items
            target_categories = target_categories - base_categories
            
            # Get recommendations for each target category
            recommendations = {}
            for category in target_categories:
                recs = self.faiss_manager.search(
                    query_embedding=avg_embedding,
                    k=k_per_category,
                    filter_user_id=user_id,
                    filter_categories=[category],
                    exclude_item_id=None,  # Could exclude base items
                    min_similarity=0.5
                )
                recommendations[category] = recs
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting outfit recommendations: {e}")
            raise
    
    async def _store_embedding_backup(self, item_id: str, embedding):
        """Store embedding in Supabase as backup (optional)"""
        if not self.supabase:
            return  # Skip if Supabase not configured
        
        try:
            # Store as JSON array in a text column or use pgvector extension
            # This is optional - FAISS is the primary store
            embedding_list = embedding.tolist()
            
            # Update clothes table with embedding (if column exists)
            # You'd need to add an embedding column to your schema
            # For now, we'll skip this or store in a separate embeddings table
            
        except Exception as e:
            logger.warning(f"Could not store embedding backup: {e}")
    
    async def remove_item(self, item_id: str) -> bool:
        """Remove item from index"""
        return self.faiss_manager.remove_item(item_id)
    
    def get_stats(self) -> Dict:
        """Get service statistics"""
        stats = {
            'faiss_stats': self.faiss_manager.get_stats(),
            'model': settings.fashion_clip_model,
            'device': settings.device,
            'supabase_configured': self.supabase is not None
        }
        return stats

