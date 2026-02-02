from pydantic import BaseModel, Field
from typing import List, Optional


class ParsedJD(BaseModel):
    
    role: str = Field(..., description="Job title/role")

    must_have_skills: List[str] = Field(default_factory=list, description="Required skills")

    nice_to_have_skills: List[str] = Field(default_factory=list, description="Preferred skills")

    min_experience_years: float = Field(default=0, description="Minimum years of experience")

    max_experience_years: Optional[float] = Field(default=None, description="Maximum years (if specified)")

    domain: str = Field(default="", description="Industry/domain (e.g., SaaS, Fintech)")

    tech_stack: List[str] = Field(default_factory=list, description="Tools and technologies")
    
    summary: str = Field(default="", description="Brief summary for embedding")
