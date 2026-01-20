from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Development mode (skip Firebase)
    dev_mode: bool = True
    
    # OpenAI
    openai_api_key: str = "sk-mock-key-for-dev"
    
    # Firebase
    firebase_project_id: str = "mock-project"
    google_application_credentials: str = "/app/service-account.json"
    
    # Weaviate
    weaviate_url: str = "http://weaviate:8080"
    
    # Ollama
    ollama_url: str = "http://ollama:11434"
    ollama_model: str = "llama3.2:1b"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

