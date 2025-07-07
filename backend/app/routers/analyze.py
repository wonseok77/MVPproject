"""
면접 분석 API 라우터
"""
import logging
from fastapi import APIRouter, HTTPException, status
from ..models import InterviewRequest, AnalyzeResult, ErrorResponse
from ..services.azure_openai import azure_openai_service
from ..services.chroma_store import chroma_store_service

logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter(
    prefix="/analyze",
    tags=["분석"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)

@router.post("/interview", response_model=AnalyzeResult)
async def analyze_interview(request: InterviewRequest):
    """
    면접 분석 API
    
    Args:
        request: 면접 분석 요청 데이터
        
    Returns:
        AnalyzeResult: 분석 결과
    """
    try:
        logger.info(f"면접 분석 요청 수신: {request.candidate_name}, {request.position}")
        
        # 1. Azure OpenAI를 사용한 면접 분석
        analysis_result = azure_openai_service.analyze_interview(
            candidate_name=request.candidate_name,
            position=request.position,
            resume_text=request.resume_text,
            job_posting_text=request.job_posting_text,
            interview_text=request.interview_text
        )
        
        logger.info(f"면접 분석 완료: {request.candidate_name}")
        
        # 2. ChromaDB에 결과 저장
        document_id = chroma_store_service.save_analysis_result(
            candidate_name=request.candidate_name,
            position=request.position,
            summary=analysis_result["summary"],
            strengths=analysis_result["strengths"],
            weaknesses=analysis_result["weaknesses"]
        )
        
        logger.info(f"분석 결과 저장 완료: {document_id}")
        
        # 3. 결과 반환
        return AnalyzeResult(
            id=document_id,
            candidate_name=request.candidate_name,
            position=request.position,
            summary=analysis_result["summary"],
            strengths=analysis_result["strengths"],
            weaknesses=analysis_result["weaknesses"]
        )
        
    except Exception as e:
        logger.error(f"면접 분석 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"면접 분석 실패: {str(e)}"
        )

@router.get("/result/{document_id}", response_model=AnalyzeResult)
async def get_analysis_result(document_id: str):
    """
    저장된 분석 결과 조회
    
    Args:
        document_id: 문서 ID
        
    Returns:
        AnalyzeResult: 분석 결과
    """
    try:
        logger.info(f"분석 결과 조회 요청: {document_id}")
        
        # ChromaDB에서 결과 조회
        result = chroma_store_service.get_analysis_result(document_id)
        
        return AnalyzeResult(
            id=result["id"],
            candidate_name=result["candidate_name"],
            position=result["position"],
            summary=result["summary"],
            strengths=result["strengths"],
            weaknesses=result["weaknesses"]
        )
        
    except Exception as e:
        logger.error(f"분석 결과 조회 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"분석 결과를 찾을 수 없습니다: {str(e)}"
        )

@router.get("/search")
async def search_analyses(query: str, limit: int = 10):
    """
    분석 결과 검색
    
    Args:
        query: 검색 쿼리
        limit: 결과 제한 수
        
    Returns:
        list: 검색 결과
    """
    try:
        logger.info(f"분석 결과 검색 요청: {query}")
        
        # ChromaDB에서 검색
        results = chroma_store_service.search_analyses(query, limit)
        
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        logger.error(f"분석 결과 검색 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"검색 실패: {str(e)}"
        )

@router.get("/stats")
async def get_collection_stats():
    """
    컬렉션 통계 정보 조회
    
    Returns:
        dict: 통계 정보
    """
    try:
        logger.info("컬렉션 통계 조회 요청")
        
        # ChromaDB 통계 조회
        stats = chroma_store_service.get_collection_stats()
        
        return stats
        
    except Exception as e:
        logger.error(f"통계 조회 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"통계 조회 실패: {str(e)}"
        ) 