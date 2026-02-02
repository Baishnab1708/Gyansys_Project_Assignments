"""
Semantic Match - cosine similarity between JD and resume embeddings.
"""
from typing import List
from app.embeddings import embedder


def compute_semantic_score(jd_summary: str, resume_summary: str) -> float:
    """
    Compute semantic similarity between JD and resume.
    
    Args:
        jd_summary: JD summary text
        resume_summary: Resume summary text
        
    Returns:
        Similarity score (0-1)
    """
    jd_embedding = embedder.embed_text(jd_summary)
    resume_embedding = embedder.embed_text(resume_summary)
    
    return embedder.cosine_similarity(jd_embedding, resume_embedding)


def batch_semantic_scores(jd_summary: str, resume_summaries: List[str]) -> List[float]:
    """
    Compute semantic scores for multiple resumes.
    
    Args:
        jd_summary: JD summary text
        resume_summaries: List of resume summary texts
        
    Returns:
        List of similarity scores
    """
    jd_embedding = embedder.embed_text(jd_summary)
    resume_embeddings = embedder.embed_texts(resume_summaries)
    
    return [
        embedder.cosine_similarity(jd_embedding, re)
        for re in resume_embeddings
    ]
