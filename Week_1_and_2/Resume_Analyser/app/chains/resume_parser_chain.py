"""
Resume Parser Chain - extracts structured candidate profiles from resumes.
"""
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.config import settings
from app.schemas import ParsedResume


RESUME_PARSER_PROMPT = """You are an expert resume analyst. Extract structured information from this resume.

Resume Text:
{resume_text}

Extract the following:
1. Candidate's full name
2. Email (if visible)
3. All technical and soft skills
4. Total years of professional experience
5. Notable projects (name, brief description, technologies used)
6. Education details (degrees, institutions)
7. Past company names
8. A 2-3 sentence summary highlighting key strengths for job matching

Be thorough but only extract what's explicitly stated or clearly implied."""


class ResumeParserChain:
    """Chain for parsing resumes into structured candidate profiles."""
    
    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_deployment=settings.azure.openai_deployment,
            azure_endpoint=settings.azure.openai_endpoint,
            api_key=settings.azure.openai_api_key,
            api_version=settings.azure.openai_api_version,
            temperature=0,
            max_retries=5
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert resume analyst extracting candidate information."),
            ("human", RESUME_PARSER_PROMPT)
        ])
        
        # Structured output chain
        self.chain = self.prompt | self.llm.with_structured_output(ParsedResume)
    
    def parse(self, resume_text: str, candidate_id: str) -> ParsedResume:
        """Parse resume text into structured profile."""
        result = self.chain.invoke({"resume_text": resume_text})
        result.candidate_id = candidate_id
        result.raw_text = resume_text
        return result


# Singleton instance
resume_parser_chain = ResumeParserChain()
