"""
Parsed Resume/Candidate schema.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class Project(BaseModel):
    """Individual project details."""
    
    name: str = Field(..., description="Project name")
    description: str = Field(default="", description="Brief description")
    technologies: List[str] = Field(default_factory=list, description="Tech used")


class ParsedResume(BaseModel):
    """Structured candidate profile after LLM parsing."""
    
    candidate_id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Candidate name")
    email: Optional[str] = Field(default=None, description="Email if found")
    skills: List[str] = Field(default_factory=list, description="All skills extracted")
    experience_years: float = Field(default=0, description="Total years of experience")
    projects: List[Project] = Field(default_factory=list, description="Notable projects")
    education: List[str] = Field(default_factory=list, description="Education details")
    companies: List[str] = Field(default_factory=list, description="Past companies")
    summary: str = Field(default="", description="Brief summary for embedding")
    raw_text: str = Field(default="", description="Original resume text")
