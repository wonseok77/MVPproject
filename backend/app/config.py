"""
환경변수 기반 설정 파일
"""
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# 프로젝트 루트의 .env 파일 로드 (간단한 절대경로)
import pathlib
project_root = pathlib.Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=str(env_path))

class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # Azure OpenAI 설정
    azure_openai_api_key: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    azure_openai_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    azure_openai_deployment_name: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
    azure_openai_api_version: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")
    azure_openai_model_1: str = os.getenv("AZURE_OPENAI_MODEL_1", "dev-gpt-4o")
    azure_openai_embedding_model: str = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    
    # Azure AI Search 설정
    azure_ai_search_service_name: str = os.getenv("AZURE_AI_SEARCH_SERVICE_NAME", "")
    azure_ai_search_api_key: str = os.getenv("AZURE_AI_SEARCH_API_KEY", "")
    azure_ai_search_index_name: str = os.getenv("AZURE_AI_SEARCH_INDEX_NAME", "")
    
    # Azure Storage 설정
    azure_storage_account_name: str = os.getenv("AZURE_STORAGE_ACCOUNT_NAME", "")
    azure_storage_account_key: str = os.getenv("AZURE_STORAGE_ACCOUNT_KEY", "")
    azure_storage_container_name: str = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "documents")
    
    # Azure Speech Service 설정
    azure_speech_key: str = os.getenv("AZURE_SPEECH_KEY", "")
    azure_speech_region: str = os.getenv("AZURE_SPEECH_REGION", "koreacentral")
    azure_speech_endpoint: str = os.getenv("AZURE_SPEECH_ENDPOINT", "")
    
    # Azure OpenAI Transcription 설정 (면접 STT용)
    azureopenai_endpoint: str = os.getenv("AZUREOPENAI_ENDPOINT", "")
    azureopenai_key: str = os.getenv("AZUREOPENAI_KEY", "")
    azureopenai_api_version: str = os.getenv("AZUREOPENAI_API_VERSION", "2024-05-01-preview")
    azureopenai_transcription_model: str = os.getenv("AZUREOPENAI_TRANSCRIPTION_MODEL", "gpt-4o-transcribe")
    
    # Azure Form Recognizer 설정
    azure_form_key: str = os.getenv("AZURE_FORM_KEY", "")
    azure_form_endpoint: str = os.getenv("AZURE_FORM_ENDPOINT", "")
    
    # ChromaDB 설정
    chroma_persist_dir: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    
    # 기타 설정
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "info")
    
    class Config:
        # 프로젝트 루트의 .env 파일 경로 설정
        env_file = str(env_path)
        env_file_encoding = "utf-8"

# 전역 설정 인스턴스
settings = Settings() 