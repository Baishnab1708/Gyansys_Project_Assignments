import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # LLM Provider: "openai" or "azure"
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
    
    # OpenAI Settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Azure OpenAI Settings
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    # Pipeline Settings
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")
