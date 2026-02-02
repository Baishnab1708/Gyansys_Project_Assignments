"""
Reranker Chain - final ranking with LLM reasoning.
"""
from typing import List
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from app.config import settings
from app.schemas import ParsedJD, RankedCandidate


class RerankedResult(BaseModel):
    """Single reranked candidate."""
    candidate_id: str
    rank: int
    reason: str = Field(description="Brief reason for this ranking position")


class RerankerOutput(BaseModel):
    """Reranker chain output."""
    rankings: List[RerankedResult]


RERANKER_PROMPT = """You are a senior recruiter making final hiring recommendations.

## Job Requirements:
Role: {role}
Must-Have Skills: {must_have_skills}
Domain: {domain}
Experience: {min_experience}+ years

## Candidates with Scores:
{candidates_summary}

Based on the scores AND your understanding of role fit, provide a final ranking.
Consider:
- Must-have skill coverage is critical
- Domain experience matters for senior roles
- Balance between overqualified and underqualified
- Growth potential for borderline candidates

Rank all candidates from 1 (best fit) to N (least fit).
Provide a brief reason for each ranking position."""


class RerankerChain:
    """Chain for final candidate reranking."""
    
    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_deployment=settings.azure.openai_deployment,
            azure_endpoint=settings.azure.openai_endpoint,
            api_key=settings.azure.openai_api_key,
            api_version=settings.azure.openai_api_version,
            temperature=0.2,
            max_retries=5
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a senior recruiter making final hiring decisions."),
            ("human", RERANKER_PROMPT)
        ])
        
        self.chain = self.prompt | self.llm.with_structured_output(RerankerOutput)
    
    def rerank(
        self,
        jd: ParsedJD,
        candidates: List[RankedCandidate]
    ) -> List[RerankedResult]:
        """Rerank candidates with LLM reasoning."""
        
        # Build candidate summary
        summaries = []
        for c in candidates:
            summary = f"""
- {c.name} (ID: {c.candidate_id})
  Score: {c.final_score:.1f}/100
  Signals: Semantic={c.signals.semantic_score:.2f}, Skill={c.signals.skill_match_score:.2f}, Exp={c.signals.experience_score:.2f}, Project={c.signals.project_relevance_score:.2f}
  Evaluation: {c.evaluation.fit_summary if c.evaluation else 'N/A'}
"""
            summaries.append(summary)
        
        result = self.chain.invoke({
            "role": jd.role,
            "must_have_skills": ", ".join(jd.must_have_skills),
            "domain": jd.domain,
            "min_experience": jd.min_experience_years,
            "candidates_summary": "\n".join(summaries)
        })
        
        return result.rankings


# Singleton instance
reranker_chain = RerankerChain()
