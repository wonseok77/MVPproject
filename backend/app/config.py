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

# 🔥 기존 환경변수 무시하고 .env 파일 우선 적용
load_dotenv(dotenv_path=str(env_path), override=True)

# 디버깅: .env 파일 로드 확인
print(f"🔍 .env 파일 경로: {env_path}")
print(f"🔍 .env 파일 존재?: {env_path.exists()}")
if env_path.exists():
    print("✅ .env 파일이 override=True로 로드되었습니다")

class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # Azure OpenAI 설정 (.env의 AZURE_OPENAI_* 와 매핑)
    azure_openai_api_key: str = ""
    azure_openai_endpoint: str = ""
    azure_openai_deployment_name: str = "gpt-4o-eastus2"
    azure_openai_api_version: str = "2024-12-01-preview"
    azure_openai_model_1: str = "gpt-4o-eastus2" 
    azure_openai_embedding_model: str = "text-embedding-3-small-eastus2"
    
    # Azure AI Search 설정 (.env의 AZURE_AI_SEARCH_* 와 매핑)
    azure_ai_search_service_name: str = ""
    azure_ai_search_api_key: str = ""
    azure_ai_search_index_name: str = ""
    
    # Azure Storage 설정 (.env의 AZURE_STORAGE_* 와 매핑)
    azure_storage_account_name: str = ""
    azure_storage_account_key: str = ""
    azure_storage_container_name: str = ""
    
    # Azure Speech Service 설정 (.env의 AZURE_SPEECH_* 와 매핑)
    azure_speech_key: str = ""
    azure_speech_region: str = "koreacentral"
    azure_speech_endpoint: str = ""
    
    # Azure OpenAI Transcription 설정 (STT용) - GPT-4o-transcribe 전용
    azureopenai_endpoint: str = "https://user04-openai-eastus2.openai.azure.com/"  # Base URL (고정값)
    azureopenai_key: str = ""  # .env에서 로드
    azureopenai_api_version: str = "2025-01-01-preview"  # GPT-4o-transcribe 실제 지원 버전 (Azure Playground 확인됨)
    azureopenai_transcription_model: str = "gpt-4o-transcribe-eastus2"  # 실제 deployment 이름
    
    # Azure Form Recognizer 설정 (.env의 AZURE_FORM_* 와 매핑)
    azure_form_key: str = ""
    azure_form_endpoint: str = ""
    
    # ChromaDB 설정 (.env의 CHROMA_* 와 매핑)
    chroma_persist_dir: str = "./chroma_db"
    
    # 기타 설정
    debug: bool = False
    log_level: str = "info"
    
    class Config:
        # 프로젝트 루트의 .env 파일 경로 설정
        env_file = str(env_path)
        env_file_encoding = "utf-8"
        # 추가 필드 허용 (환경변수에서 오는 값들)
        extra = "allow"
        # 대소문자 구분하지 않음 (AZURE_OPENAI_API_KEY → azure_openai_api_key)
        case_sensitive = False

# 전역 설정 인스턴스
settings = Settings()

# 🔍 디버깅: 실제 로드된 값들 확인
print("=" * 50)
print("🔍 settings 인스턴스에 로드된 실제 값들:")
print(f"azure_openai_endpoint: {settings.azure_openai_endpoint}")
print(f"azure_openai_deployment_name: {settings.azure_openai_deployment_name}")
print(f"azure_openai_api_version: {settings.azure_openai_api_version}")
print(f"azure_ai_search_service_name: {settings.azure_ai_search_service_name}")
print(f"azure_storage_account_name: {settings.azure_storage_account_name}")
print(f"azureopenai_endpoint: {settings.azureopenai_endpoint}")
print(f"azureopenai_key: {settings.azureopenai_key[:20]}..." if settings.azureopenai_key else "azureopenai_key: (비어있음)")
print(f"azureopenai_api_version: {settings.azureopenai_api_version}")
print("=" * 50) 