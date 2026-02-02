"""
Qdrant Vector Store for Resume Storage with Query-Time Slicing.

Stores full embeddings (768 dims) and performs two-stage search:
- Stage 1: 256-dim slice for fast candidate retrieval
- Stage 2: Full-dim rerank for precision
"""
from typing import List, Tuple, Optional
from pathlib import Path
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams, Distance, PointStruct, 
    Filter, FieldCondition, MatchValue
)

from app.embeddings.matryoshka_embedder import matryoshka_embedder
from app.loaders import load_resume_from_pdf
from app.utils import clean_text


class QdrantResumeStore:
    """Qdrant-based resume vector store with query-time slicing."""
    
    COLLECTION_NAME = "resumes"
    VECTOR_DIM = 768  # gte-modernbert-base dimension
    
    DEFAULT_PERSIST_PATH = "./qdrant_data"
    
    def __init__(self, persist_path: Optional[str] = "./qdrant_data"):
        """
        Initialize Qdrant client with disk persistence.
        
        Args:
            persist_path: Path for disk persistence. Default = ./qdrant_data
        """
        self.persist_path = persist_path
        self.client = QdrantClient(path=persist_path)
        
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Create collection if not exists."""
        collections = self.client.get_collections().collections
        exists = any(c.name == self.COLLECTION_NAME for c in collections)
        
        if not exists:
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=self.VECTOR_DIM,
                    distance=Distance.COSINE
                )
            )
    
    def ingest_resumes(self, resume_folder: str) -> int:
        """
        Load all resumes from folder and store in Qdrant.
        
        Args:
            resume_folder: Path to folder containing PDF/DOCX resumes
            
        Returns:
            Number of resumes ingested
        """
        from app.loaders.resume_loader import load_resume_from_pdf, load_resume_from_docx_bytes
        
        folder = Path(resume_folder)
        if not folder.exists():
            raise ValueError(f"Resume folder not found: {resume_folder}")
        
        # Find all resume files
        resume_files = list(folder.glob("*.pdf")) + list(folder.glob("*.docx"))
        
        if not resume_files:
            print(f"No resume files found in {resume_folder}")
            return 0
        
        points = []
        texts = []
        
        for idx, filepath in enumerate(resume_files):
            try:
                # Load and clean text
                if filepath.suffix.lower() == ".pdf":
                    raw_text = load_resume_from_pdf(filepath)
                else:
                    with open(filepath, "rb") as f:
                        raw_text = load_resume_from_docx_bytes(f.read())
                
                cleaned_text = clean_text(raw_text)
                texts.append(cleaned_text)
                
                # Store metadata
                points.append({
                    "id": idx,
                    "filename": filepath.name,
                    "filepath": str(filepath),
                    "text": cleaned_text[:5000]  # Store truncated for retrieval
                })
            except Exception as e:
                print(f"Error loading {filepath.name}: {e}")
                continue
        
        if not texts:
            return 0
        
        # Batch embed all texts
        embeddings = matryoshka_embedder.embed_texts(texts)
        
        # Create Qdrant points
        qdrant_points = [
            PointStruct(
                id=p["id"],
                vector=embeddings[i].tolist(),
                payload={
                    "filename": p["filename"],
                    "filepath": p["filepath"],
                    "text": p["text"]
                }
            )
            for i, p in enumerate(points)
        ]
        
        # Upsert to Qdrant
        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=qdrant_points
        )
        
        print(f"Ingested {len(qdrant_points)} resumes into Qdrant")
        return len(qdrant_points)
    
    def search_resumes(
        self, 
        jd_text: str, 
        top_k_stage1: int = 7,
        top_k_final: int = 4
    ) -> List[Tuple[str, str, float]]:
        """
        Two-stage matryoshka search:
        Stage 1: 256-dim slice search (fast) -> top_k_stage1
        Stage 2: Full 768-dim search on stage1 results -> top_k_final
        """
        collection_info = self.client.get_collection(self.COLLECTION_NAME)
        total_points = collection_info.points_count
        
        if total_points == 0:
            return []
        
        # Embed JD once
        jd_embedding = matryoshka_embedder.embed_text(jd_text)
        
        # Fetch ALL vectors from Qdrant (batch retrieve for speed)
        all_records = self.client.scroll(
            collection_name=self.COLLECTION_NAME,
            limit=total_points,
            with_vectors=True,
            with_payload=True
        )[0]
        
        if not all_records:
            return []
        
        # Extract vectors and payloads
        ids = [r.id for r in all_records]
        vectors = np.array([r.vector for r in all_records])
        payloads = [r.payload for r in all_records]
        
        # If few resumes, skip two-stage
        if total_points <= top_k_final:
            similarities = np.dot(vectors, jd_embedding)
            top_indices = np.argsort(similarities)[::-1]
            return [
                (payloads[i]["filename"], payloads[i]["text"], float(similarities[i]))
                for i in top_indices
            ]
        
        # ==========================================
        # STAGE 1: 256-dim slice search (FAST)
        # ==========================================
        jd_256 = jd_embedding[:256]
        jd_256 = jd_256 / np.linalg.norm(jd_256)
        
        vectors_256 = vectors[:, :256]
        vectors_256 = vectors_256 / np.linalg.norm(vectors_256, axis=1, keepdims=True)
        
        similarities_256 = np.dot(vectors_256, jd_256)
        top_7_indices = np.argsort(similarities_256)[::-1][:top_k_stage1]
        
        # ==========================================
        # STAGE 2: Full 768-dim search on top 7
        # ==========================================
        jd_full = jd_embedding / np.linalg.norm(jd_embedding)
        
        stage2_candidates = []
        for idx in top_7_indices:
            full_vec = vectors[idx]
            full_vec_norm = full_vec / np.linalg.norm(full_vec)
            
            similarity_full = float(np.dot(full_vec_norm, jd_full))
            
            stage2_candidates.append({
                "idx": idx,
                "filename": payloads[idx]["filename"],
                "text": payloads[idx]["text"],
                "score_256": float(similarities_256[idx]),
                "score_full": similarity_full
            })
        
        # Sort by full-dim score and take top_k_final
        stage2_candidates.sort(key=lambda x: x["score_full"], reverse=True)
        top_4 = stage2_candidates[:top_k_final]
        
        return [(c["filename"], c["text"], c["score_full"]) for c in top_4]
    
    def get_resume_text(self, filename: str) -> Optional[str]:
        """Get full resume text by filename."""
        results = self.client.scroll(
            collection_name=self.COLLECTION_NAME,
            scroll_filter=Filter(
                must=[FieldCondition(key="filename", match=MatchValue(value=filename))]
            ),
            limit=1,
            with_payload=True
        )
        
        if results[0]:
            return results[0][0].payload.get("text")
        return None
    
    def clear(self):
        """Clear all resumes from the store."""
        self.client.delete_collection(self.COLLECTION_NAME)
        self._ensure_collection()
        print("Cleared all resumes from Qdrant")


# Default store instance (disk persistent)
resume_store = QdrantResumeStore(persist_path="./qdrant_data")
