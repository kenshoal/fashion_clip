"""
FashionCLIP embedding model wrapper
"""
import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import numpy as np
from typing import Union
import logging

logger = logging.getLogger(__name__)


class FashionCLIPEmbedder:
    """
    Wrapper for FashionCLIP model to generate image embeddings
    """
    
    def __init__(self, model_name: str = "patrickjohncyh/fashion-clip", device: str = "cpu"):
        """
        Initialize FashionCLIP model
        
        Args:
            model_name: HuggingFace model identifier
            device: Device to run on ('cpu' or 'cuda')
        """
        self.model_name = model_name
        self.device = device if torch.cuda.is_available() and device == "cuda" else "cpu"
        
        logger.info(f"Loading FashionCLIP model: {model_name} on {self.device}")
        
        # Load model and processor
        self.model = CLIPModel.from_pretrained(model_name).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(model_name)
        
        # Set to evaluation mode
        self.model.eval()
        
        logger.info("FashionCLIP model loaded successfully")
    
    def get_image_embedding(self, image: Union[Image.Image, np.ndarray]) -> np.ndarray:
        """
        Generate embedding for an image
        
        Args:
            image: PIL Image or numpy array
            
        Returns:
            Normalized embedding vector (512 dimensions)
        """
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        
        # Process image
        inputs = self.processor(images=image, return_tensors="pt", padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Generate embedding
        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)
            # Normalize to unit vector for cosine similarity
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        
        # Convert to numpy and return first (and only) embedding
        embedding = image_features.cpu().numpy()[0]
        
        return embedding
    
    def get_text_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for text (optional, for text-to-image search)
        
        Args:
            text: Text description
            
        Returns:
            Normalized embedding vector (512 dimensions)
        """
        inputs = self.processor(text=text, return_tensors="pt", padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            text_features = self.model.get_text_features(**inputs)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
        
        embedding = text_features.cpu().numpy()[0]
        
        return embedding

