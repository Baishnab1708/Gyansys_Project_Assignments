from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.config import settings
from app.schemas import ParsedJD


JD_PARSER_PROMPT = """You are an expert recruiter. Analyze this job description and extract structured requirements.

Job Description:
{jd_text}

Extract the following information:
1. Role/Job Title
2. Must-have skills (absolutely required)
3. Nice-to-have skills (preferred but optional)
4. Minimum years of experience
5. Maximum years of experience (if mentioned)
6. Domain/Industry
7. Tech stack and tools
8. A brief 2-3 sentence summary for semantic matching

Be precise and extract only what's explicitly stated or strongly implied."""


class JDParserChain:

    
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
            ("system", "You are an expert recruiter analyzing job descriptions."),
            ("human", JD_PARSER_PROMPT)
        ])
        
        # Structured output chain
        self.chain = self.prompt | self.llm.with_structured_output(ParsedJD)
    
    def parse(self, jd_text: str) -> ParsedJD:
        return self.chain.invoke({"jd_text": jd_text})


# Singleton instance
jd_parser_chain = JDParserChain()
