"""
문서 분석 API 라우터 - 파일 업로드 및 분석
"""
import logging
import datetime
import json
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

@router.post("/integrated-analysis")
async def integrated_analysis_api(request: dict):
    """
    2단계 시연용: 문서 분석 + 면접 STT 통합 분석
    
    Args:
        request: {
            "document_analysis": "1단계 문서 분석 결과",
            "interview_stt": "면접 STT 결과",
            "resume_filename": "이력서 파일명",
            "job_filename": "채용공고 파일명"
        }
        
    Returns:
        dict: 최종 종합 평가 결과
    """
    try:
        document_analysis = request.get("document_analysis", "")
        interview_stt = request.get("interview_stt", "")
        resume_filename = request.get("resume_filename", "")
        job_filename = request.get("job_filename", "")
        
        logger.info("🔄 2단계: 문서+면접 통합 분석 시작")
        
        if not document_analysis or not interview_stt:
            return {
                "status": "error",
                "message": "문서 분석 결과와 면접 STT 결과가 모두 필요합니다."
            }
        
        # 통합 분석 프롬프트
        prompt = f"""
당신은 전문 채용 컨설턴트입니다. 아래 1단계 서류 심사 결과와 2단계 면접 결과를 종합하여 최종 평가를 해주세요.

## 📋 1단계: 서류 심사 결과
{document_analysis}

## 🎤 2단계: 면접 내용 (STT 결과)
{interview_stt}

---

아래 형식으로 **최종 종합 평가**를 작성해주세요:

## 🎯 최종 종합 평가

### 📊 단계별 평가 요약
- **서류 심사**: [1단계 결과 요약] 
- **면접 평가**: [면접 내용 기반 평가]
- **종합 점수**: XX/100점

### ✅ 최종 강점
1. [서류+면접에서 확인된 핵심 강점]
2. [일관성 있게 나타난 역량]
3. [특별히 인상적인 부분]

### ⚠️ 최종 우려사항
1. [서류와 면접에서 발견된 gap]
2. [보완 필요한 영역]
3. [추가 검증 필요한 부분]

### 💼 채용 권고사항
- **최종 권고**: [채용 강력 추천/조건부 추천/보류/불합격]
- **배치 추천 부서**: [구체적 부서명 + 이유]
- **온보딩 시 주의사항**: [신입사원 적응을 위한 조언]

### 🎯 면접관을 위한 추가 확인 질문
1. [기술적 깊이 확인 질문]
2. [동기/열정 확인 질문]
3. [팀 적합성 확인 질문]

### 📈 성장 가능성 및 장기 전망
[해당 지원자의 3-5년 후 성장 가능성과 회사 기여도 예측]
"""
        
        # LLM을 통한 통합 분석
        result = document_analyzer.llm.invoke(prompt)
        
        return {
            "status": "success",
            "analysis_type": "integrated",
            "input_summary": {
                "document_analysis_length": len(document_analysis),
                "interview_stt_length": len(interview_stt),
                "resume_file": resume_filename,
                "job_file": job_filename
            },
            "integrated_analysis": result.content
        }
        
    except Exception as e:
        logger.error(f"❌ 통합 분석 중 오류: {str(e)}")
        return {
            "status": "error",
            "message": f"통합 분석 실패: {str(e)}"
        }

@router.post("/save-analysis-result")
async def save_analysis_result_api(request: dict):
    """
    분석 결과를 Azure Blob Storage에 JSON 파일로 저장
    
    Args:
        request: {
            "metadata": {
                "saved_at": "2024-01-15T10:30:00Z",
                "resume_file": "이력서 파일명",
                "job_file": "채용공고 파일명", 
                "analysis_type": "document | integrated"
            },
            "results": {
                "document_analysis": "문서 분석 결과",
                "interview_stt": "면접 STT 결과",
                "integrated_analysis": "통합 분석 결과"
            }
        }
        
    Returns:
        dict: 저장 결과
    """
    try:
        logger.info("💾 분석 결과 저장 요청")
        
        # 요청 데이터 검증
        if not request.get("metadata") or not request.get("results"):
            return {
                "status": "error",
                "message": "metadata와 results가 필요합니다."
            }
        
        # 파일명 생성 (타임스탬프 기반)
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        analysis_type = request["metadata"].get("analysis_type", "unknown")
        filename = f"analysis_result_{analysis_type}_{timestamp}.json"
        
        # JSON 데이터 준비
        save_data = {
            "metadata": request["metadata"],
            "results": request["results"],
            "saved_info": {
                "filename": filename,
                "saved_at": datetime.datetime.now().isoformat(),
                "file_size": len(str(request))
            }
        }
        
        # JSON 문자열로 변환
        import json
        json_content = json.dumps(save_data, ensure_ascii=False, indent=2)
        json_bytes = json_content.encode('utf-8')
        
        # Azure Blob Storage에 저장
        result = document_analyzer.upload_file_to_storage(json_bytes, filename)
        
        if result["status"] == "success":
            logger.info(f"✅ 분석 결과 저장 완료: {filename}")
            return {
                "status": "success",
                "message": "분석 결과가 성공적으로 저장되었습니다.",
                "filename": filename,
                "saved_at": save_data["saved_info"]["saved_at"],
                "file_size": save_data["saved_info"]["file_size"]
            }
        else:
            logger.error(f"❌ 분석 결과 저장 실패: {result['message']}")
            return {
                "status": "error",
                "message": f"저장 실패: {result['message']}"
            }
        
    except Exception as e:
        logger.error(f"❌ 분석 결과 저장 중 오류: {str(e)}")
        return {
            "status": "error",
            "message": f"저장 중 오류: {str(e)}"
        }

@router.get("/get-saved-results")
async def get_saved_results_api():
    """
    저장된 분석 결과 목록 조회
    
    Returns:
        dict: 저장된 결과 파일 목록
    """
    try:
        logger.info("📋 저장된 분석 결과 목록 조회")
        
        # 전체 파일 목록 조회
        files_result = document_analyzer.get_blob_files_list()
        
        if files_result["status"] != "success":
            return {
                "status": "error",
                "message": "파일 목록 조회 실패"
            }
        
        # 분석 결과 파일들만 필터링 (analysis_result_로 시작하는 파일들)
        all_files = files_result.get("files", [])
        result_files = []
        
        for file_info in all_files:
            filename = file_info.get("name", "")
            if filename.startswith("analysis_result_") and filename.endswith(".json"):
                # 메타데이터 추출 시도
                try:
                    # 파일명에서 정보 추출
                    parts = filename.replace("analysis_result_", "").replace(".json", "").split("_")
                    if len(parts) >= 2:
                        analysis_type = parts[0]
                        timestamp = "_".join(parts[1:])
                        
                        result_files.append({
                            "filename": filename,
                            "metadata": {
                                "analysis_type": analysis_type,
                                "timestamp": timestamp,
                                "saved_at": file_info.get("last_modified", ""),
                                "file_size": file_info.get("size", 0)
                            }
                        })
                except Exception as e:
                    logger.warning(f"파일명 파싱 오류: {filename} - {str(e)}")
                    # 기본 정보만 추가
                    result_files.append({
                        "filename": filename,
                        "metadata": {
                            "analysis_type": "unknown",
                            "timestamp": "",
                            "saved_at": file_info.get("last_modified", ""),
                            "file_size": file_info.get("size", 0)
                        }
                    })
        
        # 최신 순으로 정렬
        result_files.sort(key=lambda x: x["metadata"]["saved_at"], reverse=True)
        
        logger.info(f"✅ 저장된 분석 결과 {len(result_files)}개 발견")
        return {
            "status": "success",
            "total_results": len(result_files),
            "results": result_files
        }
        
    except Exception as e:
        logger.error(f"❌ 저장된 결과 목록 조회 중 오류: {str(e)}")
        return {
            "status": "error",
            "message": f"목록 조회 실패: {str(e)}"
        }

@router.get("/load-analysis-result/{filename}")
async def load_analysis_result_api(filename: str):
    """
    저장된 분석 결과 불러오기
    
    Args:
        filename: 불러올 결과 파일명
        
    Returns:
        dict: 저장된 분석 결과 데이터
    """
    try:
        logger.info(f"📂 분석 결과 불러오기: {filename}")
        
        # 파일명 검증
        if not filename.startswith("analysis_result_") or not filename.endswith(".json"):
            return {
                "status": "error",
                "message": "올바른 분석 결과 파일이 아닙니다."
            }
        
        # Azure Blob Storage에서 파일 읽기
        if document_analyzer.blob_service_client is None:
            return {
                "status": "error",
                "message": "Azure Storage가 설정되지 않았습니다."
            }
        
        blob_client = document_analyzer.blob_service_client.get_blob_client(
            container=document_analyzer.container_name,
            blob=filename
        )
        
        # 파일 다운로드
        try:
            blob_data = blob_client.download_blob()
            json_content = blob_data.readall().decode('utf-8')
            
            # JSON 파싱
            import json
            result_data = json.loads(json_content)
            
            logger.info(f"✅ 분석 결과 불러오기 완료: {filename}")
            return {
                "status": "success",
                "filename": filename,
                "data": result_data,
                "loaded_at": datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            if "BlobNotFound" in str(e):
                return {
                    "status": "error",
                    "message": "파일을 찾을 수 없습니다."
                }
            else:
                raise e
        
    except Exception as e:
        logger.error(f"❌ 분석 결과 불러오기 중 오류: {str(e)}")
        return {
            "status": "error",
            "message": f"불러오기 실패: {str(e)}"
        }

@router.delete("/delete-analysis-result/{filename}")
async def delete_analysis_result_api(filename: str):
    """
    저장된 분석 결과 삭제
    
    Args:
        filename: 삭제할 결과 파일명
        
    Returns:
        dict: 삭제 결과
    """
    try:
        logger.info(f"🗑️ 분석 결과 삭제: {filename}")
        
        # 파일명 검증
        if not filename.startswith("analysis_result_") or not filename.endswith(".json"):
            return {
                "status": "error",
                "message": "올바른 분석 결과 파일이 아닙니다."
            }
        
        # Azure Blob Storage에서 파일 삭제
        if document_analyzer.blob_service_client is None:
            return {
                "status": "error",
                "message": "Azure Storage가 설정되지 않았습니다."
            }
        
        blob_client = document_analyzer.blob_service_client.get_blob_client(
            container=document_analyzer.container_name,
            blob=filename
        )
        
        # 파일 삭제
        try:
            blob_client.delete_blob()
            
            logger.info(f"✅ 분석 결과 삭제 완료: {filename}")
            return {
                "status": "success",
                "message": "분석 결과가 성공적으로 삭제되었습니다.",
                "filename": filename,
                "deleted_at": datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            if "BlobNotFound" in str(e):
                return {
                    "status": "error",
                    "message": "파일을 찾을 수 없습니다."
                }
            else:
                raise e
        
    except Exception as e:
        logger.error(f"❌ 분석 결과 삭제 중 오류: {str(e)}")
        return {
            "status": "error",
            "message": f"삭제 실패: {str(e)}"
        } 