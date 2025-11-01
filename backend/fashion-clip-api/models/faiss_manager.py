"""
FAISS vector index manager for similarity search
"""
import faiss
import numpy as np
import pickle
import json
from pathlib import Path
from typing import List, Dict, Optional
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class FAISSManager:
    """
    Manages FAISS vector index for storing and searching item embeddings
    """
    
    def __init__(self, index_path: str = "./data/faiss_index.bin", dimension: int = 512):
        """
        Initialize FAISS manager
        
        Args:
            index_path: Path to store/load FAISS index
            dimension: Embedding dimension (512 for FashionCLIP)
        """
        self.index_path = Path(index_path)
        self.metadata_path = Path(index_path).with_suffix('.metadata.pkl')
        self.dimension = dimension
        
        # Create directory if needed
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize index (Inner Product for cosine similarity with normalized vectors)
        self.index = faiss.IndexFlatIP(dimension)
        
        # Metadata storage: FAISS ID -> item metadata
        self.metadata: Dict[int, Dict] = {}
        
        # Item ID -> FAISS ID mapping (for removal)
        self.item_id_to_faiss_id: Dict[str, int] = {}
        
        # Counter for next FAISS ID
        self.next_id = 0
        
        # Load existing index if it exists
        self._load_index()
    
    def _load_index(self):
        """Load existing FAISS index and metadata from disk"""
        try:
            if self.index_path.exists():
                logger.info(f"Loading FAISS index from {self.index_path}")
                self.index = faiss.read_index(str(self.index_path))
                self.next_id = self.index.ntotal
                
                # Load metadata
                if self.metadata_path.exists():
                    with open(self.metadata_path, 'rb') as f:
                        data = pickle.load(f)
                        self.metadata = data.get('metadata', {})
                        self.item_id_to_faiss_id = data.get('item_id_to_faiss_id', {})
                
                logger.info(f"Loaded {self.next_id} items from index")
            else:
                logger.info("No existing index found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            logger.info("Starting with fresh index")
            self.index = faiss.IndexFlatIP(self.dimension)
            self.metadata = {}
            self.item_id_to_faiss_id = {}
            self.next_id = 0
    
    def _save_index(self):
        """Save FAISS index and metadata to disk"""
        try:
            logger.info(f"Saving FAISS index to {self.index_path}")
            faiss.write_index(self.index, str(self.index_path))
            
            # Save metadata
            data = {
                'metadata': self.metadata,
                'item_id_to_faiss_id': self.item_id_to_faiss_id
            }
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(data, f)
            
            logger.info(f"Saved index with {self.index.ntotal} items")
        except Exception as e:
            logger.error(f"Error saving index: {e}")
            raise
    
    def add_item(self, embedding: np.ndarray, metadata: Dict) -> int:
        """
        Add item to FAISS index
        
        Args:
            embedding: Normalized embedding vector
            metadata: Item metadata (must include 'item_id')
            
        Returns:
            FAISS ID assigned to the item
        """
        item_id = metadata.get('item_id')
        if not item_id:
            raise ValueError("metadata must include 'item_id'")
        
        # Check if item already exists
        if item_id in self.item_id_to_faiss_id:
            faiss_id = self.item_id_to_faiss_id[item_id]
            logger.warning(f"Item {item_id} already exists at FAISS ID {faiss_id}, updating...")
            # Remove old entry (we'll add new one)
            self._remove_by_faiss_id(faiss_id)
        
        # Ensure embedding is normalized and right shape
        if isinstance(embedding, list):
            embedding = np.array(embedding, dtype=np.float32)
        
        embedding = embedding.astype(np.float32)
        if embedding.ndim == 1:
            embedding = embedding.reshape(1, -1)
        
        # Normalize if not already normalized
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        # Add to index
        faiss_id = self.next_id
        self.index.add(embedding)
        
        # Store metadata
        self.metadata[faiss_id] = metadata
        self.item_id_to_faiss_id[item_id] = faiss_id
        self.next_id += 1
        
        # Save index
        self._save_index()
        
        logger.info(f"Added item {item_id} to index at FAISS ID {faiss_id}")
        return faiss_id
    
    def search(
        self,
        query_embedding: np.ndarray,
        k: int = 10,
        filter_user_id: Optional[str] = None,
        filter_categories: Optional[List[str]] = None,
        exclude_item_id: Optional[str] = None,
        min_similarity: float = 0.0
    ) -> List[Dict]:
        """
        Search for similar items
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            filter_user_id: Only return items for this user
            filter_categories: Only return items in these categories
            exclude_item_id: Exclude this item from results
            min_similarity: Minimum similarity score (0-1)
            
        Returns:
            List of dicts with item metadata and similarity score
        """
        if self.index.ntotal == 0:
            return []
        
        # Prepare query embedding
        if isinstance(query_embedding, list):
            query_embedding = np.array(query_embedding, dtype=np.float32)
        
        query_embedding = query_embedding.astype(np.float32)
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        # Normalize
        norm = np.linalg.norm(query_embedding)
        if norm > 0:
            query_embedding = query_embedding / norm
        
        # Search (get more results to account for filtering)
        search_k = min(k * 5, self.index.ntotal)  # Get 5x results to filter
        if search_k == 0:
            search_k = min(100, self.index.ntotal)
        
        distances, indices = self.index.search(query_embedding, search_k)
        
        # Filter and format results
        results = []
        seen_item_ids = set()
        
        if exclude_item_id:
            seen_item_ids.add(exclude_item_id)
        
        for distance, faiss_id in zip(distances[0], indices[0]):
            if faiss_id == -1:  # FAISS returns -1 for empty slots
                continue
            
            # Get metadata
            metadata = self.metadata.get(faiss_id)
            if not metadata:
                continue
            
            item_id = metadata.get('item_id')
            if not item_id or item_id in seen_item_ids:
                continue
            
            # Apply filters
            if filter_user_id and metadata.get('user_id') != filter_user_id:
                continue
            
            if filter_categories and metadata.get('category') not in filter_categories:
                continue
            
            # Check similarity threshold (distance is inner product for normalized vectors)
            similarity = float(distance)
            if similarity < min_similarity:
                continue
            
            results.append({
                'item_id': item_id,
                'similarity': similarity,
                **metadata
            })
            
            seen_item_ids.add(item_id)
            
            if len(results) >= k:
                break
        
        return results
    
    def remove_item(self, item_id: str) -> bool:
        """
        Remove item from index
        
        Note: FAISS doesn't support deletion directly. This marks the item
        as removed in metadata but doesn't free the index slot.
        For production, consider rebuilding index periodically.
        
        Args:
            item_id: Item ID to remove
            
        Returns:
            True if item was found and removed
        """
        if item_id not in self.item_id_to_faiss_id:
            return False
        
        faiss_id = self.item_id_to_faiss_id[item_id]
        self._remove_by_faiss_id(faiss_id)
        self._save_index()
        
        logger.info(f"Removed item {item_id} from index")
        return True
    
    def _remove_by_faiss_id(self, faiss_id: int):
        """Remove item by FAISS ID (internal method)"""
        if faiss_id in self.metadata:
            item_id = self.metadata[faiss_id].get('item_id')
            if item_id:
                del self.item_id_to_faiss_id[item_id]
            del self.metadata[faiss_id]
    
    def get_stats(self) -> Dict:
        """Get index statistics"""
        total_items = len(self.item_id_to_faiss_id)
        categories = defaultdict(int)
        users = set()
        
        for metadata in self.metadata.values():
            category = metadata.get('category', 'unknown')
            categories[category] += 1
            user_id = metadata.get('user_id')
            if user_id:
                users.add(user_id)
        
        return {
            'total_items': total_items,
            'index_size': self.index.ntotal,
            'dimension': self.dimension,
            'categories': dict(categories),
            'unique_users': len(users),
            'index_path': str(self.index_path)
        }

