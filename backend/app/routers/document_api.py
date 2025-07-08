"""
문서 분석 API 라우터 - 파일 업로드 및 분석
"""
import logging
from fastapi import APIRouter, HTTPException, status, UploadFile, File
from ..services.document_analyzer import (
    upload_resume_file, 
    upload_job_posting_file, 
    analyze_candidate_match,
    document_analyzer,
    get_storage_files_list
)

logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter(
    prefix="/document",
    tags=["문서분석"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)

@router.post("/upload-resume")
async def upload_resume_api(file: UploadFile = File(...)):
    """
    이력서 파일 업로드 (1단계)
    
    Args:
        file: 이력서 파일 (PDF, Word 등)
        
    Returns:
        dict: 업로드 결과 (파일명 포함)
    """
    try:
        filename = file.filename or "unknown_resume.pdf"
        logger.info(f"이력서 업로드 요청: {filename}")
        
        # 파일 내용 읽기
        file_content = await file.read()
        
        # Azure Blob Storage에 업로드
        result = upload_resume_file(file_content, filename)
        
        logger.info(f"이력서 업로드 완료: {result}")
        return result
        
    except Exception as e:
        logger.error(f"이력서 업로드 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"이력서 업로드 실패: {str(e)}"
        )

@router.post("/upload-job")
async def upload_job_posting_api(file: UploadFile = File(...)):
    """
    채용공고 파일 업로드 (1단계)
    
    Args:
        file: 채용공고 파일 (PDF, Word 등)
        
    Returns:
        dict: 업로드 결과 (파일명 포함)
    """
    try:
        filename = file.filename or "unknown_job.pdf"
        logger.info(f"채용공고 업로드 요청: {filename}")
        
        # 파일 내용 읽기
        file_content = await file.read()
        
        # Azure Blob Storage에 업로드
        result = upload_job_posting_file(file_content, filename)
        
        logger.info(f"채용공고 업로드 완료: {result}")
        return result
        
    except Exception as e:
        logger.error(f"채용공고 업로드 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"채용공고 업로드 실패: {str(e)}"
        )

@router.post("/analyze-files")
async def analyze_files_api(resume_filename: str, job_filename: str):
    """
    업로드된 파일들로 분석 실행 (2단계)
    
    Args:
        resume_filename: 이력서 파일명
        job_filename: 채용공고 파일명
        
    Returns:
        dict: 분석 결과 (적합도, 강점, 우려사항, 추천질문 포함)
    """
    try:
        logger.info(f"파일 분석 요청: {resume_filename} vs {job_filename}")
        
        # 파일 기반 분석 실행
        result = analyze_candidate_match(resume_filename, job_filename)
        
        logger.info("파일 분석 완료")
        return result
        
    except Exception as e:
        logger.error(f"파일 분석 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일 분석 실패: {str(e)}"
        )

@router.post("/analyze-text")
async def analyze_text_api(resume_text: str, job_posting_text: str):
    """
    직접 텍스트로 분석 (파일 없이)
    
    Args:
        resume_text: 지원자 이력서 내용
        job_posting_text: 채용공고 내용
        
    Returns:
        dict: 분석 결과 (적합도, 강점, 우려사항, 추천질문 포함)
    """
    try:
        logger.info("직접 텍스트 분석 요청")
        
        # 직접 텍스트 분석
        result = document_analyzer.analyze_match(resume_text, job_posting_text)
        
        logger.info("직접 텍스트 분석 완료")
        return result
        
    except Exception as e:
        logger.error(f"텍스트 분석 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"텍스트 분석 실패: {str(e)}"
        )

@router.post("/upload-both")
async def upload_both_files_api(
    resume_file: UploadFile = File(...),
    job_file: UploadFile = File(...)
):
    """
    이력서 + 채용공고 동시 업로드 (편의 기능)
    
    Args:
        resume_file: 이력서 파일
        job_file: 채용공고 파일
        
    Returns:
        dict: 두 파일 업로드 결과
    """
    try:
        resume_filename = resume_file.filename or "unknown_resume.pdf"
        job_filename = job_file.filename or "unknown_job.pdf"
        logger.info(f"동시 업로드 요청: {resume_filename}, {job_filename}")
        
        # 파일 내용 읽기
        resume_content = await resume_file.read()
        job_content = await job_file.read()
        
        # 각각 업로드
        resume_result = upload_resume_file(resume_content, resume_filename)
        job_result = upload_job_posting_file(job_content, job_filename)
        
        result = {
            "resume_upload": resume_result,
            "job_upload": job_result,
            "status": "success" if resume_result["status"] == "success" and job_result["status"] == "success" else "error"
        }
        
        logger.info("동시 업로드 완료")
        return result
        
    except Exception as e:
        logger.error(f"동시 업로드 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"동시 업로드 실패: {str(e)}"
        )

@router.post("/upload-and-analyze")
async def upload_and_analyze_api(
    resume_file: UploadFile = File(...),
    job_file: UploadFile = File(...)
):
    """
    파일 업로드 + 분석 한 번에 처리 (올인원 기능)
    
    Args:
        resume_file: 이력서 파일
        job_file: 채용공고 파일
        
    Returns:
        dict: 업로드 결과 + 분석 결과
    """
    try:
        resume_filename = resume_file.filename or "unknown_resume.pdf"
        job_filename = job_file.filename or "unknown_job.pdf"
        logger.info(f"업로드+분석 요청: {resume_filename}, {job_filename}")
        
        # 파일 내용 읽기
        resume_content = await resume_file.read()
        job_content = await job_file.read()
        
        # 1단계: 업로드
        resume_upload = upload_resume_file(resume_content, resume_filename)
        job_upload = upload_job_posting_file(job_content, job_filename)
        
        if resume_upload["status"] != "success" or job_upload["status"] != "success":
            return {
                "status": "error",
                "message": "파일 업로드 실패",
                "resume_upload": resume_upload,
                "job_upload": job_upload
            }
        
        # 2단계: 분석 (인덱싱 완료 대기)
        from ..services.document_analyzer import wait_for_file_indexing
        import time
        
        print(f"⏳ 인덱싱 대기 중: {resume_filename}, {job_filename}")
        
        # 각 파일의 인덱싱 완료 대기 (최대 60초)
        resume_indexed = wait_for_file_indexing(f"resume_{resume_filename}", 60)
        job_indexed = wait_for_file_indexing(f"job_{job_filename}", 60)
        
        print(f"📋 인덱싱 상태 - 이력서: {resume_indexed}, 채용공고: {job_indexed}")
        
        if not resume_indexed or not job_indexed:
            return {
                "status": "error",
                "message": f"파일 인덱싱이 완료되지 않았습니다. 이력서: {resume_indexed}, 채용공고: {job_indexed}",
                "upload_results": {
                    "resume_upload": resume_upload,
                    "job_upload": job_upload
                }
            }
        
        analysis_result = analyze_candidate_match(resume_filename, job_filename)
        
        result = {
            "status": "success",
            "upload_results": {
                "resume_upload": resume_upload,
                "job_upload": job_upload
            },
            "analysis_result": analysis_result
        }
        
        logger.info("업로드+분석 완료")
        return result
        
    except Exception as e:
        logger.error(f"업로드+분석 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"업로드+분석 실패: {str(e)}"
        ) 

@router.get("/files-list")
async def get_files_list_api():
    """
    Azure Blob Storage에 있는 파일 목록 조회
    
    Returns:
        dict: 이력서 및 채용공고 파일 목록
    """
    try:
        logger.info("파일 목록 조회 요청")
        
        result = get_storage_files_list()
        
        logger.info(f"파일 목록 조회 완료: {result.get('total_files', 0)}개")
        return result
        
    except Exception as e:
        logger.error(f"파일 목록 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일 목록 조회 실패: {str(e)}"
        ) 