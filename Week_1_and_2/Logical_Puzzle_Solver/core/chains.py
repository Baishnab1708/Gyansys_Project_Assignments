import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from config import Config

def load_prompt(filename: str) -> str:
    path = os.path.join(Config.PROMPTS_DIR, filename)
    with open(path, "r") as f:
        return f.read()

def create_chain(llm, prompt_file: str):
    """Create a LangChain chain with JSON output parsing."""
    template = load_prompt(prompt_file)
    prompt = ChatPromptTemplate.from_template(template)
    parser = JsonOutputParser()
    return prompt | llm | parser
