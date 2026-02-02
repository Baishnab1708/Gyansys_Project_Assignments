from langchain_openai import ChatOpenAI, AzureChatOpenAI
from config import Config

def get_llm():
    """Get the LLM based on configuration."""
    if Config.LLM_PROVIDER == "azure":
        return AzureChatOpenAI(
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
            api_key=Config.AZURE_OPENAI_API_KEY,
            api_version=Config.AZURE_OPENAI_API_VERSION,
            deployment_name=Config.AZURE_OPENAI_DEPLOYMENT,
            temperature=Config.TEMPERATURE
        )
    else:
        return ChatOpenAI(
            api_key=Config.OPENAI_API_KEY,
            model=Config.OPENAI_MODEL,
            temperature=Config.TEMPERATURE
        )
