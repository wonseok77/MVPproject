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
        # Azure OpenAI 클라이언트 설정 (STT용) - GPT-4o-transcribe 전용
        # 🔧 .env 파일 설정값 사용
        stt_endpoint = settings.azureopenai_endpoint or "https://user04-openai-eastus2.openai.azure.com/"
        stt_key = settings.azureopenai_key or settings.azure_openai_api_key
        stt_api_version = settings.azureopenai_api_version  # .env에서 로드: 2025-03-20
        self.stt_model = settings.azureopenai_transcription_model  # .env에서 로드: gpt-4o-transcribe-eastus2
            
        print(f"🔧 STT용 Azure OpenAI 설정 (.env 파일 연동):")
        print(f"   Endpoint: {stt_endpoint}")
        print(f"   API Key: {stt_key[:10]}...{stt_key[-5:] if stt_key else 'NONE'}")
        print(f"   API Version: {stt_api_version}")
        print(f"   Model: {self.stt_model}")
        
        self.openai_client = openai.AzureOpenAI(
            api_key=stt_key,
            api_version=stt_api_version,
            azure_endpoint=stt_endpoint
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
        processing_status = "UNKNOWN"
        file_status = "UNKNOWN"
        api_status = "UNKNOWN"
        
        try:
            logger.info(f"STT 시작: {filename}")
            
            # 1단계: 파일 처리
            processing_status = "파일 처리 중"
            print(f"📋 [1단계] 파일 처리 시작: {filename}")
            
            # 원본 파일 확장자 추출
            file_ext = os.path.splitext(filename)[1].lower()
            if not file_ext:
                file_ext = ".wav"  # 기본값
            
            # 🎵 모든 파일 타입 직접 지원 (Azure Playground 확인됨)
            print(f"🎵 {file_ext} 파일 - Azure OpenAI 직접 지원")
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            file_status = f"{file_ext} 파일 처리 완료 (직접 지원)"
            
            print(f"✅ [1단계] 파일 처리 성공: {file_status}")
            processing_status = "API 호출 준비 중"
            
            try:
                # 2단계: Azure OpenAI API 호출
                print(f"📋 [2단계] Azure OpenAI API 호출 시작")
                print(f"   🎯 모델: gpt-4o-transcribe-eastus2")
                print(f"   📁 파일: {temp_file_path}")
                print(f"   🌏 언어: ko")
                print(f"   🔗 API 버전: 2025-03-20")
                
                processing_status = "Azure OpenAI API 호출 중"
                api_status = "API 호출 전송 중"
                
                # 🔥 gpt-4o-transcribe-eastus2 모델만 사용
                with open(temp_file_path, "rb") as audio_file:
                    transcript = self.openai_client.audio.transcriptions.create(
                        model=self.stt_model,  # .env에서 로드된 모델명 사용
                        file=audio_file,
                        language="ko"
                    )
                
                api_status = "API 호출 성공"
                transcribed_text = transcript.text
                print(f"✅ [2단계] Azure OpenAI API 호출 성공")
                print(f"🎯 사용된 모델: gpt-4o-transcribe-eastus2")
                print(f"📝 변환된 텍스트 길이: {len(transcribed_text)}자")
                logger.info(f"STT 완료 (모델: gpt-4o-transcribe-eastus2): {len(transcribed_text)}자")
                
                processing_status = "완료"
                
                return {
                    "status": "success",
                    "transcription": transcribed_text,
                    "filename": filename,
                    "text_length": len(transcribed_text),
                    "processing_status": processing_status,
                    "file_status": file_status,
                    "api_status": api_status
                }
                
            finally:
                # 임시 파일 삭제
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            # 단계별 오류 분석
            error_stage = "알 수 없음"
            if "404" in str(e) or "Resource not found" in str(e):
                error_stage = "Azure OpenAI API 호출 단계"
                api_status = "API 호출 실패 (404 - 리소스 없음)"
                processing_status = "API 오류로 실패"
            elif "FileNotFoundError" in str(e):
                error_stage = "파일 처리 단계"
                file_status = "파일 처리 실패"
                processing_status = "파일 오류로 실패"
            elif "Azure" in str(e):
                error_stage = "Azure 서비스 연결 단계"
                api_status = "Azure 연결 실패"
                processing_status = "연결 오류로 실패"
            else:
                error_stage = processing_status
            
            print(f"💥 [오류 발생] 단계: {error_stage}")
            print(f"💥 오류 타입: {type(e).__name__}")
            print(f"💥 오류 메시지: {str(e)}")
            print(f"📊 처리 상태: {processing_status}")
            print(f"📁 파일 상태: {file_status}")
            print(f"🔗 API 상태: {api_status}")
            
            import traceback
            print(f"💥 상세 스택 트레이스:\n{traceback.format_exc()}")
            
            logger.error(f"STT 오류 ({error_stage}): {str(e)}")
            
            # 사용자 친화적 에러 메시지 생성
            if "404" in str(e):
                user_message = "Azure OpenAI 모델을 찾을 수 없습니다. 모델 deployment 설정을 확인해주세요."
            elif "FileNotFoundError" in str(e):
                user_message = "파일 처리 중 오류가 발생했습니다. 파일 형식을 확인해주세요."
            else:
                user_message = f"음성 변환 중 오류 발생: {str(e)}"
            
            return {
                "status": "error",
                "message": user_message,
                "error_stage": error_stage,
                "processing_status": processing_status,
                "file_status": file_status,
                "api_status": api_status,
                "technical_error": str(e)
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