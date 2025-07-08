"""
문서 분석 API 라우터 - 파일 업로드 및 분석
"""
import logging
from fastapi import APIRouter, HTTPException, status, UploadFile, File
from pydantic import BaseModel
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

class AnalyzeFilesRequest(BaseModel):
    resume_filename: str
    job_filename: str

@router.post("/analyze-files")
async def analyze_files_api(request: AnalyzeFilesRequest):
    """
    업로드된 파일들로 분석 실행 (2단계)
    
    Args:
        request: 분석 요청 데이터 (이력서 파일명, 채용공고 파일명)
        
    Returns:
        dict: 분석 결과 (적합도, 강점, 우려사항, 추천질문 포함)
    """
    try:
        logger.info(f"파일 분석 요청: {request.resume_filename} vs {request.job_filename}")
        
        # 파일 기반 분석 실행
        result = analyze_candidate_match(request.resume_filename, request.job_filename)
        
        logger.info("파일 분석 완료")
        return result
        
    except Exception as e:
        logger.error(f"파일 분석 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일 분석 실패: {str(e)}"
        )

class AnalyzeTextRequest(BaseModel):
    resume_text: str
    job_posting_text: str

@router.post("/analyze-text")
async def analyze_text_api(request: AnalyzeTextRequest):
    """
    직접 텍스트로 분석 (파일 없이)
    
    Args:
        request: 분석 요청 데이터 (이력서 내용, 채용공고 내용)
        
    Returns:
        dict: 분석 결과 (적합도, 강점, 우려사항, 추천질문 포함)
    """
    try:
        logger.info("직접 텍스트 분석 요청")
        
        # 직접 텍스트 분석
        result = document_analyzer.analyze_match(request.resume_text, request.job_posting_text)
        
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
    파일 업로드 + 분석 한 번에 처리 (올인원 기능) - 시연용 최적화
    
    Args:
        resume_file: 이력서 파일
        job_file: 채용공고 파일
        
    Returns:
        dict: 업로드 결과 + 분석 결과
    """
    try:
        resume_filename = resume_file.filename or "unknown_resume.pdf"
        job_filename = job_file.filename or "unknown_job.pdf"
        logger.info(f"🚀 업로드+분석 요청: {resume_filename}, {job_filename}")
        
        # 파일 내용 읽기
        resume_content = await resume_file.read()
        job_content = await job_file.read()
        
        # 1단계: 업로드
        logger.info("📤 1단계: 파일 업로드 중...")
        resume_upload = upload_resume_file(resume_content, resume_filename)
        job_upload = upload_job_posting_file(job_content, job_filename)
        
        if resume_upload["status"] != "success" or job_upload["status"] != "success":
            return {
                "status": "error",
                "message": "파일 업로드 실패",
                "resume_upload": resume_upload,
                "job_upload": job_upload
            }
        
        # 2단계: 인덱서 즉시 실행 (시연용 최적화)
        logger.info("⚡ 2단계: 인덱서 즉시 실행 중...")
        indexer_result = document_analyzer.run_indexer()
        logger.info(f"   인덱서 실행 결과: {indexer_result.get('status', 'unknown')}")
        
        # 3단계: 인덱스 재발견 (새로운 인덱스가 생성될 수 있음)
        logger.info("🔍 3단계: 최신 인덱스 재발견 중...")
        old_index = document_analyzer.index_name
        document_analyzer.index_name = document_analyzer._get_active_index_name()
        
        # 검색 클라이언트도 새로운 인덱스로 업데이트
        from azure.search.documents import SearchClient
        document_analyzer.search_client = SearchClient(
            endpoint=document_analyzer.search_endpoint,
            index_name=document_analyzer.index_name,
            credential=document_analyzer.search_credential
        )
        
        if old_index != document_analyzer.index_name:
            logger.info(f"   인덱스 변경: {old_index} → {document_analyzer.index_name}")
        else:
            logger.info(f"   기존 인덱스 유지: {document_analyzer.index_name}")
        
        # 4단계: 인덱싱 완료 대기
        logger.info("⏳ 4단계: 인덱싱 완료 대기 중...")
        from ..services.document_analyzer import wait_for_file_indexing
        import time
        
        # 각 파일의 인덱싱 완료 대기 (시연용: 최대 30초)
        resume_indexed = wait_for_file_indexing(f"resume_{resume_filename}", 30)
        job_indexed = wait_for_file_indexing(f"job_{job_filename}", 30)
        
        logger.info(f"   인덱싱 상태 - 이력서: {resume_indexed}, 채용공고: {job_indexed}")
        
        # 5단계: 분석 실행 (인덱싱 상태와 관계없이 시도)
        logger.info("📊 5단계: 분석 실행 중...")
        if not resume_indexed or not job_indexed:
            logger.warning("⚠️ 인덱싱 미완료 상태에서 분석 시도...")
            
        analysis_result = analyze_candidate_match(resume_filename, job_filename)
        
        result = {
            "status": "success",
            "upload_results": {
                "resume_upload": resume_upload,
                "job_upload": job_upload
            },
            "indexer_result": indexer_result,
            "index_info": {
                "old_index": old_index,
                "new_index": document_analyzer.index_name,
                "index_changed": old_index != document_analyzer.index_name
            },
            "indexing_status": {
                "resume_indexed": resume_indexed,
                "job_indexed": job_indexed
            },
            "analysis_result": analysis_result
        }
        
        logger.info("✅ 업로드+분석 완료!")
        return result
        
    except Exception as e:
        logger.error(f"❌ 업로드+분석 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"업로드+분석 실패: {str(e)}"
        )

@router.post("/upload-and-analyze-fast")
async def upload_and_analyze_fast_api(
    resume_file: UploadFile = File(...),
    job_file: UploadFile = File(...)
):
    """
    파일 업로드 + 분석 한 번에 처리 (시연용 고속 모드)
    인덱싱 대기 시간을 최소화하여 빠른 시연이 가능합니다.
    
    Args:
        resume_file: 이력서 파일
        job_file: 채용공고 파일
        
    Returns:
        dict: 업로드 결과 + 분석 결과
    """
    try:
        resume_filename = resume_file.filename or "unknown_resume.pdf"
        job_filename = job_file.filename or "unknown_job.pdf"
        logger.info(f"🚀 고속 업로드+분석 요청: {resume_filename}, {job_filename}")
        
        # 파일 내용 읽기
        resume_content = await resume_file.read()
        job_content = await job_file.read()
        
        # 1단계: 업로드
        logger.info("📤 1단계: 파일 업로드 중...")
        resume_upload = upload_resume_file(resume_content, resume_filename)
        job_upload = upload_job_posting_file(job_content, job_filename)
        
        if resume_upload["status"] != "success" or job_upload["status"] != "success":
            return {
                "status": "error",
                "message": "파일 업로드 실패",
                "resume_upload": resume_upload,
                "job_upload": job_upload
            }
        
        # 2단계: 인덱서 즉시 실행
        logger.info("⚡ 2단계: 인덱서 실행 중...")
        indexer_result = document_analyzer.run_indexer()
        logger.info(f"   인덱서 실행 결과: {indexer_result.get('status', 'unknown')}")
        
        # 3단계: 인덱스 재발견
        logger.info("🔍 3단계: 최신 인덱스 재발견 중...")
        old_index = document_analyzer.index_name
        document_analyzer.index_name = document_analyzer._get_active_index_name()
        
        # 검색 클라이언트 업데이트
        from azure.search.documents import SearchClient
        document_analyzer.search_client = SearchClient(
            endpoint=document_analyzer.search_endpoint,
            index_name=document_analyzer.index_name,
            credential=document_analyzer.search_credential
        )
        
        if old_index != document_analyzer.index_name:
            logger.info(f"   인덱스 변경: {old_index} → {document_analyzer.index_name}")
        else:
            logger.info(f"   기존 인덱스 유지: {document_analyzer.index_name}")
        
        # 4단계: 짧은 인덱싱 대기 (시연용: 최대 10초)
        logger.info("⏳ 4단계: 빠른 인덱싱 확인 중...")
        from ..services.document_analyzer import wait_for_file_indexing
        import time
        
        resume_indexed = wait_for_file_indexing(f"resume_{resume_filename}", 10)
        job_indexed = wait_for_file_indexing(f"job_{job_filename}", 10)
        
        logger.info(f"   빠른 인덱싱 상태 - 이력서: {resume_indexed}, 채용공고: {job_indexed}")
        
        # 5단계: 즉시 분석 실행
        logger.info("📊 5단계: 즉시 분석 실행 중...")
        analysis_result = analyze_candidate_match(resume_filename, job_filename)
        
        result = {
            "status": "success",
            "mode": "fast",
            "upload_results": {
                "resume_upload": resume_upload,
                "job_upload": job_upload
            },
            "indexer_result": indexer_result,
            "index_info": {
                "old_index": old_index,
                "new_index": document_analyzer.index_name,
                "index_changed": old_index != document_analyzer.index_name
            },
            "indexing_status": {
                "resume_indexed": resume_indexed,
                "job_indexed": job_indexed,
                "wait_time": "10_seconds_max"
            },
            "analysis_result": analysis_result
        }
        
        logger.info("✅ 고속 업로드+분석 완료!")
        return result
        
    except Exception as e:
        logger.error(f"❌ 고속 업로드+분석 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"고속 업로드+분석 실패: {str(e)}"
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

@router.get("/debug-index")
async def debug_index_api():
    """
    Azure AI Search 인덱스 디버깅 (개발용)
    
    Returns:
        dict: 인덱스 스키마와 모든 문서 정보
    """
    try:
        logger.info("인덱스 디버깅 요청")
        
        result = document_analyzer.debug_search_index()
        
        logger.info("인덱스 디버깅 완료")
        return result
        
    except Exception as e:
        logger.error(f"인덱스 디버깅 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"인덱스 디버깅 실패: {str(e)}"
        ) 

@router.post("/run-indexer")
async def run_indexer_api():
    """
    Azure AI Search 인덱서를 수동으로 실행 (Blob Storage → AI Search 동기화)
    
    Returns:
        dict: 인덱서 실행 결과
    """
    try:
        logger.info("인덱서 수동 실행 요청")
        
        result = document_analyzer.run_indexer()
        
        logger.info(f"인덱서 실행 완료: {result}")
        return result
        
    except Exception as e:
        logger.error(f"인덱서 실행 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"인덱서 실행 실패: {str(e)}"
        )

@router.get("/indexer-status")
async def get_indexer_status_api():
    """
    Azure AI Search 인덱서 상태 확인
    
    Returns:
        dict: 모든 인덱서의 상태 정보
    """
    try:
        logger.info("인덱서 상태 확인 요청")
        
        result = document_analyzer.check_indexer_status()
        
        logger.info("인덱서 상태 확인 완료")
        return result
        
    except Exception as e:
        logger.error(f"인덱서 상태 확인 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"인덱서 상태 확인 실패: {str(e)}"
        ) 