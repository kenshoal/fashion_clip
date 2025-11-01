"""
Models package for FashionCLIP API
"""
from .embedding_model import FashionCLIPEmbedder
from .faiss_manager import FAISSManager

__all__ = ['FashionCLIPEmbedder', 'FAISSManager']

