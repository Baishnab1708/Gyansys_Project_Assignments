from typing import List
from app.embeddings.matryoshka_embedder import matryoshka_embedder


def filter_resumes(jd_text: str, resume_texts: List[str], top_k_final: int = 4) -> List[int]:
   
    # If few resumes, skip filtering
    if len(resume_texts) <= top_k_final:
        return list(range(len(resume_texts)))
    
    # Embed JD and all resumes
    jd_embedding = matryoshka_embedder.embed_text(jd_text)
    resume_embeddings = matryoshka_embedder.embed_texts(resume_texts)
    
    # Stage 1: 256-dim search → top 7
    top_7_indices = matryoshka_embedder.search_256(
        jd_embedding, 
        resume_embeddings, 
        top_k=7
    )
    
    # Get embeddings for top 7 only
    top_7_embeddings = resume_embeddings[top_7_indices]
    
    # Stage 2: Full-dim search on top 7 → top 4
    top_4_relative = matryoshka_embedder.search_full(
        jd_embedding, 
        top_7_embeddings, 
        top_k=top_k_final
    )
    
    # Map back to original indices
    top_4_indices = [top_7_indices[i] for i in top_4_relative]
    
    return top_4_indices
