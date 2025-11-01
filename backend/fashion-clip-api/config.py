"""
Configuration settings for FashionCLIP API
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Server
    # Hugging Face Spaces uses dynamic ports via PORT env var
    port: int = 8000  # Default for local dev, overridden by PORT env var
    host: str = "0.0.0.0"
    debug: bool = False
    
    # Supabase (optional for demo/standalone mode)
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_service_key: str = ""
    
    # FAISS
    faiss_index_path: str = "./data/faiss_index.bin"
    faiss_index_dimension: int = 512
    embedding_cache_dir: str = "./data/embeddings_cache"
    
    # Image Upload
    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 10
    allowed_extensions: List[str] = ["jpg", "jpeg", "png", "webp"]
    
    # Model
    fashion_clip_model: str = "patrickjohncyh/fashion-clip"
    device: str = "cpu"
    batch_size: int = 4
    
    # CORS
    cors_origins: List[str] = ["http://localhost:5173"]
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        # PORT env var will automatically override port field


# Create directories
os.makedirs("data", exist_ok=True)
os.makedirs("uploads", exist_ok=True)
os.makedirs("logs", exist_ok=True)

settings = Settings()

