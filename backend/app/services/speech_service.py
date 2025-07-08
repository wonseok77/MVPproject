"""
면접 녹음 STT 및 분석 서비스
Azure OpenAI gpt-4o-transcribe 모델을 사용한 음성-텍스트 변환 및 면접 분석
"""
import os
import logging
import tempfile
from typing import Optional, Dict, Any
import openai
from azure.storage.blob import BlobServiceClient
from langchain_openai import AzureChatOpenAI
from ..config import settings

logger = logging.getLogger(__name__)

class SpeechAnalysisService:
    """면접 녹음 STT 및 분석 서비스"""
    
    def __init__(self):
        # Azure OpenAI 클라이언트 설정 (STT용)
        self.openai_client = openai.AzureOpenAI(
            api_key=settings.azureopenai_key,
            api_version=settings.azureopenai_api_version,
            azure_endpoint=settings.azureopenai_endpoint
        )
        
        # LangChain Azure OpenAI 클라이언트 (분석용)
        self.llm = AzureChatOpenAI(
            model=settings.azure_openai_deployment_name,
            temperature=0.3,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint,
            azure_deployment=settings.azure_openai_deployment_name,
        )
        
        # Azure Blob Storage 클라이언트
        if settings.azure_storage_account_name and settings.azure_storage_account_key:
            self.blob_service_client = BlobServiceClient(
                account_url=f"https://{settings.azure_storage_account_name}.blob.core.windows.net",
                credential=settings.azure_storage_account_key
            )
            self.container_name = settings.azure_storage_container_name
        else:
            self.blob_service_client = None
            self.container_name = None
    
    def upload_audio_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """면접 녹음 파일을 Azure Blob Storage에 업로드"""
        try:
            if not self.blob_service_client or not self.container_name:
                return {
                    "status": "error",
                    "message": "Azure Storage가 설정되지 않았습니다."
                }
            
            # 면접 파일명 앞에 prefix 추가
            interview_filename = f"interview_{filename}"
            
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=interview_filename
            )
            
            # 파일 업로드
            blob_client.upload_blob(file_content, overwrite=True)
            
            logger.info(f"면접 녹음 파일 업로드 완료: {interview_filename}")
            
            return {
                "status": "success",
                "message": f"면접 녹음 파일 '{interview_filename}'이 성공적으로 업로드되었습니다.",
                "filename": interview_filename
            }
        except Exception as e:
            logger.error(f"면접 녹음 파일 업로드 오류: {str(e)}")
            return {
                "status": "error",
                "message": f"면접 녹음 파일 업로드 중 오류 발생: {str(e)}"
            }
    
    def transcribe_audio(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """음성 파일을 텍스트로 변환 (STT)"""
        try:
            logger.info(f"STT 시작: {filename}")
            
            # 임시 파일로 저장 (OpenAI API는 파일 경로가 필요)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            try:
                # Azure OpenAI Whisper API 호출
                with open(temp_file_path, "rb") as audio_file:
                    transcript = self.openai_client.audio.transcriptions.create(
                        model=settings.azureopenai_transcription_model,
                        file=audio_file,
                        language="ko"  # 한국어 설정
                    )
                
                transcribed_text = transcript.text
                logger.info(f"STT 완료: {len(transcribed_text)}자")
                
                return {
                    "status": "success",
                    "transcription": transcribed_text,
                    "filename": filename,
                    "text_length": len(transcribed_text)
                }
                
            finally:
                # 임시 파일 삭제
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"STT 오류: {str(e)}")
            return {
                "status": "error",
                "message": f"음성 변환 중 오류 발생: {str(e)}"
            }
    
    def analyze_interview_content(self, transcription: str, job_description: str = "") -> Dict[str, Any]:
        """면접 내용 분석"""
        try:
            logger.info(f"면접 분석 시작: {len(transcription)}자")
            
            prompt = f"""
당신은 전문 면접관이자 HR 컨설턴트입니다. 다음 면접 내용을 분석하여 지원자를 평가해주세요.

**면접 내용:**
{transcription}

**채용공고 정보:**
{job_description if job_description else "정보 없음"}

아래 형식으로 분석해주세요:

## 🎯 면접자 종합 평가

### 📊 평가 점수
- **의사소통 능력**: XX/100점 (명확성, 논리성, 표현력)
- **기술적 역량**: XX/100점 (전문 지식, 경험, 문제해결)
- **협업 및 팀워크**: XX/100점 (소통, 협력, 리더십)
- **성장 가능성**: XX/100점 (학습 의지, 적응력, 발전성)
- **직무 적합성**: XX/100점 (직무 이해도, 경험 매칭)

### ✅ 주요 강점
1. **[구체적 강점 1]**: 상세 설명
2. **[구체적 강점 2]**: 상세 설명
3. **[구체적 강점 3]**: 상세 설명

### ⚠️ 개선 필요 사항
1. **[개선점 1]**: 구체적 개선 방안
2. **[개선점 2]**: 구체적 개선 방안
3. **[개선점 3]**: 구체적 개선 방안

### 💬 핵심 답변 분석
- **가장 인상적인 답변**: 구체적 내용과 이유
- **아쉬운 답변**: 구체적 내용과 개선점
- **추가 확인 필요 사항**: 후속 질문이나 검증 포인트

### 🎖️ 최종 채용 권고
- **채용 결정**: [강력 추천/조건부 추천/보류/불합격]
- **권고 이유**: 3-4줄 요약
- **배치 추천 부서**: 구체적 부서/팀 추천
- **성장 로드맵**: 향후 발전 방향 제시

### 📝 추가 검증 포인트
1. 레퍼런스 체크 시 확인할 사항
2. 실무 테스트 추천 영역
3. 온보딩 시 중점 지원 사항
"""
            
            result = self.llm.invoke(prompt)
            
            logger.info("면접 분석 완료")
            
            return {
                "status": "success",
                "analysis": result.content,
                "text_length": len(transcription)
            }
            
        except Exception as e:
            logger.error(f"면접 분석 오류: {str(e)}")
            return {
                "status": "error",
                "message": f"면접 분석 중 오류 발생: {str(e)}"
            }
    
    def upload_and_transcribe(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """업로드 + STT 한 번에 처리"""
        try:
            # 1단계: 파일 업로드
            upload_result = self.upload_audio_file(file_content, filename)
            if upload_result["status"] != "success":
                return upload_result
            
            # 2단계: STT 처리
            transcribe_result = self.transcribe_audio(file_content, filename)
            
            return {
                "status": "success" if transcribe_result["status"] == "success" else "error",
                "upload_result": upload_result,
                "transcribe_result": transcribe_result,
                "filename": upload_result.get("filename"),
                "transcription": transcribe_result.get("transcription", ""),
                "message": "업로드 및 STT 처리 완료" if transcribe_result["status"] == "success" else transcribe_result.get("message")
            }
            
        except Exception as e:
            logger.error(f"업로드+STT 처리 오류: {str(e)}")
            return {
                "status": "error",
                "message": f"업로드+STT 처리 중 오류 발생: {str(e)}"
            }
    
    def get_interview_files_list(self) -> Dict[str, Any]:
        """저장된 면접 녹음 파일 목록 조회"""
        try:
            if not self.blob_service_client or not self.container_name:
                return {
                    "status": "error",
                    "message": "Azure Storage가 설정되지 않았습니다."
                }
            
            container_client = self.blob_service_client.get_container_client(self.container_name)
            
            interview_files = []
            
            # interview_ prefix가 있는 파일들만 조회
            blobs = container_client.list_blobs(name_starts_with="interview_")
            
            for blob in blobs:
                # interview_ prefix 제거한 표시명
                display_name = blob.name.replace("interview_", "")
                
                interview_files.append({
                    "name": blob.name,  # 전체 파일명 (interview_포함)
                    "display_name": display_name,  # 표시용 파일명
                    "size": blob.size,
                    "last_modified": blob.last_modified.isoformat() if blob.last_modified else None
                })
            
            logger.info(f"면접 파일 목록 조회 완료: {len(interview_files)}개")
            
            return {
                "status": "success",
                "interview_files": interview_files,
                "total_files": len(interview_files)
            }
            
        except Exception as e:
            logger.error(f"면접 파일 목록 조회 오류: {str(e)}")
            return {
                "status": "error",
                "message": f"면접 파일 목록 조회 중 오류 발생: {str(e)}"
            }

# 전역 서비스 인스턴스
speech_service = SpeechAnalysisService()

# 편의 함수들
def upload_interview_file(file_content: bytes, filename: str) -> Dict[str, Any]:
    """면접 녹음 파일 업로드"""
    return speech_service.upload_audio_file(file_content, filename)

def transcribe_interview(file_content: bytes, filename: str) -> Dict[str, Any]:
    """면접 녹음 STT"""
    return speech_service.transcribe_audio(file_content, filename)

def analyze_interview(transcription: str, job_description: str = "") -> Dict[str, Any]:
    """면접 내용 분석"""
    return speech_service.analyze_interview_content(transcription, job_description)

def upload_and_transcribe_interview(file_content: bytes, filename: str) -> Dict[str, Any]:
    """업로드 + STT 한 번에"""
    return speech_service.upload_and_transcribe(file_content, filename)

def get_interview_files() -> Dict[str, Any]:
    """면접 파일 목록 조회"""
    return speech_service.get_interview_files_list() 