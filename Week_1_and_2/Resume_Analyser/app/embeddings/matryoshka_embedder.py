from typing import List, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer


class MatryoshkaEmbedder:
    
    def __init__(self, model_name: str = "Alibaba-NLP/gte-modernbert-base"):
        self.model = SentenceTransformer(model_name, trust_remote_code=True)
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        return self.model.encode(texts, normalize_embeddings=True)
    
    def embed_text(self, text: str) -> np.ndarray:
        return self.model.encode([text], normalize_embeddings=True)[0]
    
    @staticmethod
    def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        return float(np.dot(vec1, vec2))
    
    def search_256(
        self, 
        query_emb: np.ndarray, 
        embeddings: np.ndarray, 
        top_k: int = 7
    ) -> List[int]:
        

        query_256 = query_emb[:256]
        embs_256 = embeddings[:, :256]
        
        # Normalize truncated embeddings
        query_256 = query_256 / np.linalg.norm(query_256)
        embs_256 = embs_256 / np.linalg.norm(embs_256, axis=1, keepdims=True)
        
        # Compute similarities
        similarities = np.dot(embs_256, query_256)
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        return top_indices.tolist()
    
    def search_full(
        self, 
        query_emb: np.ndarray, 
        embeddings: np.ndarray, 
        top_k: int = 4
    ) -> List[int]:
    
        # Compute similarities (embeddings already normalized)
        similarities = np.dot(embeddings, query_emb)
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        return top_indices.tolist()


# Singleton instance
matryoshka_embedder = MatryoshkaEmbedder()
