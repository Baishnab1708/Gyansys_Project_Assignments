from pydantic import BaseModel, Field
from typing import List, Optional


class ScoringSignals(BaseModel):

    
    semantic_score: float = Field(default=0, description="Semantic similarity (0-1)")
    skill_match_score: float = Field(default=0, description="Skill match percentage (0-1)")
    experience_score: float = Field(default=0, description="Experience fit score (0-1)")
    project_relevance_score: float = Field(default=0, description="Project relevance (0-1)")


class CandidateEvaluation(BaseModel):
    
    
    strengths: List[str] = Field(default_factory=list, description="Key strengths")
    risks: List[str] = Field(default_factory=list, description="Potential risks/gaps")
    missing_skills: List[str] = Field(default_factory=list, description="Missing but learnable skills")
    fit_summary: str = Field(default="", description="Brief fit assessment")


class RankedCandidate(BaseModel):
    
    candidate_id: str
    name: str
    rank: int
    final_score: float = Field(description="Aggregated score (0-100)")
    signals: ScoringSignals
    evaluation: Optional[CandidateEvaluation] = None
    reason: str = Field(default="", description="Ranking reason from reranker")


class RankingResponse(BaseModel):
    
    
    jd_summary: str = Field(description="Parsed JD summary")
    total_candidates: int
    rankings: List[RankedCandidate]
