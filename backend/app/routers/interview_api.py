"""
면접 분석 API 라우터 - 음성 파일 업로드, STT, 면접 내용 분석
"""
import logging
from fastapi import APIRouter, HTTPException, status, UploadFile, File
from pydantic import BaseModel
from typing import Optional
from ..services.speech_service import (
    upload_interview_file,
    transcribe_interview,
    analyze_interview,
    upload_and_transcribe_interview,
    get_interview_files
)

logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter(
    prefix="/interview",
    tags=["면접분석"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)

@router.post("/upload-audio")
async def upload_interview_audio_api(file: UploadFile = File(...)):
    """
    면접 녹음 파일 업로드 (1단계)
    
    Args:
        file: 면접 녹음 파일 (MP3, WAV, M4A 등)
        
    Returns:
        dict: 업로드 결과 (파일명 포함)
    """
    try:
        filename = file.filename or "unknown_interview.mp3"
        logger.info(f"면접 녹음 파일 업로드 요청: {filename}")
        
        # 파일 내용 읽기
        file_content = await file.read()
        
        # Azure Blob Storage에 업로드
        result = upload_interview_file(file_content, filename)
        
        logger.info(f"면접 녹음 파일 업로드 완료: {result}")
        return result
        
    except Exception as e:
        logger.error(f"면접 녹음 파일 업로드 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"면접 녹음 파일 업로드 실패: {str(e)}"
        )

@router.post("/transcribe")
async def transcribe_audio_api(file: UploadFile = File(...)):
    """
    음성 파일 STT (Speech-to-Text) 변환
    
    Args:
        file: 음성 파일 (MP3, WAV, M4A 등)
        
    Returns:
        dict: STT 결과 (변환된 텍스트 포함)
    """
    try:
        filename = file.filename or "unknown_audio.mp3"
        logger.info(f"STT 변환 요청: {filename}")
        
        # 파일 내용 읽기
        file_content = await file.read()
        
        # Azure OpenAI Whisper API로 STT 처리
        result = transcribe_interview(file_content, filename)
        
        logger.info(f"STT 변환 완료: {result.get('status')}")
        return result
        
    except Exception as e:
        logger.error(f"STT 변환 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"STT 변환 실패: {str(e)}"
        )

@router.post("/upload-and-transcribe")
async def upload_and_transcribe_api(file: UploadFile = File(...)):
    """
    면접 녹음 업로드 + STT 한 번에 처리 (올인원 기능)
    
    Args:
        file: 면접 녹음 파일 (MP3, WAV, M4A 등)
        
    Returns:
        dict: 업로드 결과 + STT 결과
    """
    try:
        filename = file.filename or "unknown_interview.mp3"
        logger.info(f"🎤 면접 업로드+STT 요청: {filename}")
        
        # 파일 내용 읽기
        file_content = await file.read()
        
        # 업로드 + STT 한 번에 처리
        result = upload_and_transcribe_interview(file_content, filename)
        
        logger.info(f"✅ 면접 업로드+STT 완료: {result.get('status')}")
        return result
        
    except Exception as e:
        logger.error(f"❌ 면접 업로드+STT 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"면접 업로드+STT 실패: {str(e)}"
        )

class AnalyzeInterviewRequest(BaseModel):
    transcription: str
    job_description: Optional[str] = ""

@router.post("/analyze")
async def analyze_interview_api(request: AnalyzeInterviewRequest):
    """
    면접 내용 분석 (STT 결과를 바탕으로)
    
    Args:
        request: 면접 분석 요청 (STT 텍스트, 선택적 채용공고 정보)
        
    Returns:
        dict: 면접 분석 결과 (평가 점수, 강점, 개선점, 채용 권고 등)
    """
    try:
        logger.info(f"면접 내용 분석 요청: {len(request.transcription)}자")
        
        # 면접 내용 분석
        result = analyze_interview(request.transcription, request.job_description or "")
        
        logger.info("면접 내용 분석 완료")
        return result
        
    except Exception as e:
        logger.error(f"면접 내용 분석 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"면접 내용 분석 실패: {str(e)}"
        )

@router.post("/full-analysis")
async def full_interview_analysis_api(
    audio_file: UploadFile = File(...),
    job_description: str = ""
):
    """
    면접 전체 분석 (업로드 + STT + 분석) 올인원
    
    Args:
        audio_file: 면접 녹음 파일
        job_description: 채용공고 정보 (선택사항)
        
    Returns:
        dict: 업로드 → STT → 분석 전체 결과
    """
    try:
        filename = audio_file.filename or "unknown_interview.mp3"
        logger.info(f"🚀 면접 전체 분석 요청: {filename}")
        
        # 파일 내용 읽기
        file_content = await audio_file.read()
        
        # 1단계: 업로드 + STT
        upload_transcribe_result = upload_and_transcribe_interview(file_content, filename)
        
        if upload_transcribe_result["status"] != "success":
            return upload_transcribe_result
        
        transcription = upload_transcribe_result.get("transcription", "")
        
        if not transcription:
            return {
                "status": "error",
                "message": "STT 결과가 비어있습니다.",
                "upload_transcribe_result": upload_transcribe_result
            }
        
        # 2단계: 면접 내용 분석
        logger.info("📊 2단계: 면접 내용 분석 시작...")
        analysis_result = analyze_interview(transcription, job_description)
        
        result = {
            "status": "success" if analysis_result["status"] == "success" else "error",
            "upload_transcribe_result": upload_transcribe_result,
            "analysis_result": analysis_result,
            "filename": upload_transcribe_result.get("filename"),
            "transcription": transcription,
            "analysis": analysis_result.get("analysis", ""),
            "message": "면접 전체 분석 완료" if analysis_result["status"] == "success" else analysis_result.get("message")
        }
        
        logger.info("✅ 면접 전체 분석 완료!")
        return result
        
    except Exception as e:
        logger.error(f"❌ 면접 전체 분석 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"면접 전체 분석 실패: {str(e)}"
        )

@router.get("/audio-files")
async def get_interview_audio_files_api():
    """
    저장된 면접 녹음 파일 목록 조회
    
    Returns:
        dict: 면접 녹음 파일 목록
    """
    try:
        logger.info("면접 파일 목록 조회 요청")
        
        result = get_interview_files()
        
        logger.info(f"면접 파일 목록 조회 완료: {result.get('total_files', 0)}개")
        return result
        
    except Exception as e:
        logger.error(f"면접 파일 목록 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"면접 파일 목록 조회 실패: {str(e)}"
        ) 

# 기존 면접 분석 통합을 위한 편의 API들

class QuickInterviewAnalysisRequest(BaseModel):
    """빠른 면접 분석 요청 (기존 STT 결과 활용)"""
    stt_result: str
    job_posting_content: Optional[str] = ""
    resume_content: Optional[str] = ""

@router.post("/quick-analysis")
async def quick_interview_analysis_api(request: QuickInterviewAnalysisRequest):
    """
    빠른 면접 분석 (이미 있는 STT 결과 활용)
    기존 앱의 STT 결과를 바로 분석할 때 사용
    
    Args:
        request: STT 결과와 추가 정보
        
    Returns:
        dict: 면접 분석 결과
    """
    try:
        logger.info(f"빠른 면접 분석 요청: {len(request.stt_result)}자")
        
        # 채용공고 정보 결합
        context_info = ""
        if request.job_posting_content:
            context_info += f"**채용공고 정보:**\n{request.job_posting_content}\n\n"
        if request.resume_content:
            context_info += f"**지원자 이력서:**\n{request.resume_content}\n\n"
        
        # 면접 내용 분석
        result = analyze_interview(request.stt_result, context_info)
        
        logger.info("빠른 면접 분석 완료")
        return result
        
    except Exception as e:
        logger.error(f"빠른 면접 분석 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"빠른 면접 분석 실패: {str(e)}"
        ) 