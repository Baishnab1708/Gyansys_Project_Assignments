"""
Pydantic Settings for Resume Ranker.
Loads configuration from .env file.
"""
from pydantic_settings import BaseSettings
from pydantic import Field


class AzureOpenAISettings(BaseSettings):
    """Azure OpenAI configuration."""
    
    openai_endpoint: str = Field(..., description="Azure OpenAI endpoint URL")
    openai_api_key: str = Field(..., description="Azure OpenAI API key")
    openai_api_version: str = Field(default="2024-02-15-preview", description="API version")
    openai_deployment: str = Field(..., description="Chat model deployment name")
    openai_embedding_deployment: str = Field(default="text-embedding-ada-002", description="Embedding model deployment")
    
    class Config:
        env_prefix = "AZURE_"
        env_file = ".env"
        extra = "ignore"


class ScoringSettings(BaseSettings):
    """Scoring weights configuration."""
    
    semantic_weight: float = Field(default=0.40, description="Weight for semantic similarity")
    skill_weight: float = Field(default=0.30, description="Weight for skill match")
    experience_weight: float = Field(default=0.20, description="Weight for experience fit")
    project_weight: float = Field(default=0.10, description="Weight for project relevance")
    
    class Config:
        env_prefix = "SCORE_"
        env_file = ".env"
        extra = "ignore"


class Settings(BaseSettings):
    """Main application settings."""
    
    app_name: str = Field(default="Resume Ranker")
    debug: bool = Field(default=False)
    
    azure: AzureOpenAISettings = Field(default_factory=AzureOpenAISettings)
    scoring: ScoringSettings = Field(default_factory=ScoringSettings)
    
    class Config:
        env_file = ".env"
        extra = "ignore"


# Singleton instance
settings = Settings()
