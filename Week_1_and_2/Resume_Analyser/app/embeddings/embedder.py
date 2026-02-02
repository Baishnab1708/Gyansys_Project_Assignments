"""
Embedder service using local Sentence Transformers.
Uses the same model as matryoshka_embedder for consistency.
"""
from typing import List
import numpy as np
from app.embeddings.matryoshka_embedder import matryoshka_embedder


class Embedder:
    """Handles text embedding using local Sentence Transformers."""
    
    def __init__(self):
        # Reuse the matryoshka embedder's model
        self._embedder = matryoshka_embedder
    
    def embed_text(self, text: str) -> List[float]:
        """Embed a single text string."""
        embedding = self._embedder.embed_text(text)
        return embedding.tolist()
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple text strings."""
        embeddings = self._embedder.embed_texts(texts)
        return embeddings.tolist()
    
    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))


# Singleton instance
embedder = Embedder()

