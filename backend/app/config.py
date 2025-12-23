"""
Configuration management using Pydantic Settings.
Loads environment variables and provides type-safe configuration.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/disha_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # OpenRouter / LLM
    OPENROUTER_API_KEY: str
    AI_PROVIDER: str = "openai"
    AI_MODEL: str = "openai/gpt-4o-mini"
    AI_TEMPERATURE: float = 0.7
    AI_MAX_TOKENS: int = 500
    AI_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # Application
    APP_NAME: str = "Disha AI Health Coach"
    DEBUG: bool = False
    CORS_ORIGINS: str = "http://localhost:3000"
    
    # Context Management
    MAX_CONTEXT_MESSAGES: int = 15
    MAX_INPUT_TOKENS: int = 3000
    MEMORY_EXTRACTION_INTERVAL: int = 5
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
