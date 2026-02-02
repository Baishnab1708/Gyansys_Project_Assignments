from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.config import settings
from app.schemas import CandidateEvaluation, ParsedJD, ParsedResume


EVALUATOR_PROMPT = """You are a senior hiring manager evaluating a candidate against a job description.

## Job Requirements:
Role: {role}
Must-Have Skills: {must_have_skills}
Nice-to-Have Skills: {nice_to_have_skills}
Experience Required: {min_experience}+ years
Domain: {domain}

## Candidate Profile:
Name: {candidate_name}
Skills: {candidate_skills}
Experience: {candidate_experience} years
Projects: {candidate_projects}
Education: {candidate_education}

## Scoring Context:
- Semantic Match Score: {semantic_score:.2f}
- Skill Match Score: {skill_score:.2f}
- Experience Score: {experience_score:.2f}
- Project Relevance: {project_score:.2f}
- Aggregate Score: {aggregate_score:.2f}

Provide a qualitative evaluation:
1. Key strengths that make this candidate a good fit
2. Potential risks or gaps
3. Skills that are missing but could be learned
4. Brief overall fit summary (2-3 sentences)

Be honest and specific. Don't just repeat the scores."""


class LLMEvaluatorChain:
    """Chain for qualitative candidate evaluation."""
    
    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_deployment=settings.azure.openai_deployment,
            azure_endpoint=settings.azure.openai_endpoint,
            api_key=settings.azure.openai_api_key,
            api_version=settings.azure.openai_api_version,
            temperature=0.3,  # Slight creativity for nuanced evaluation
            max_retries=5
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a senior hiring manager providing candidate evaluations."),
            ("human", EVALUATOR_PROMPT)
        ])
        
        self.chain = self.prompt | self.llm.with_structured_output(CandidateEvaluation)
    
    def evaluate(
        self,
        jd: ParsedJD,
        candidate: ParsedResume,
        scores: dict
    ) -> CandidateEvaluation:
        """Evaluate a candidate against JD with scoring context."""
        
        return self.chain.invoke({
            "role": jd.role,
            "must_have_skills": ", ".join(jd.must_have_skills),
            "nice_to_have_skills": ", ".join(jd.nice_to_have_skills),
            "min_experience": jd.min_experience_years,
            "domain": jd.domain,
            "candidate_name": candidate.name,
            "candidate_skills": ", ".join(candidate.skills),
            "candidate_experience": candidate.experience_years,
            "candidate_projects": ", ".join([p.name for p in candidate.projects]),
            "candidate_education": ", ".join(candidate.education),
            "semantic_score": scores.get("semantic", 0),
            "skill_score": scores.get("skill", 0),
            "experience_score": scores.get("experience", 0),
            "project_score": scores.get("project", 0),
            "aggregate_score": scores.get("aggregate", 0)
        })


# Singleton instance
llm_evaluator_chain = LLMEvaluatorChain()
