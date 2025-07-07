"""
Pydantic 스키마 모델 정의
"""
from typing import Optional
from pydantic import BaseModel, Field

class InterviewRequest(BaseModel):
    """면접 분석 요청 모델"""
    candidate_name: str = Field(..., description="지원자 이름")
    position: str = Field(..., description="지원 직무")
    resume_text: str = Field(..., description="이력서 텍스트")
    job_posting_text: str = Field(..., description="채용공고 텍스트")
    interview_text: str = Field(..., description="면접 내용 텍스트 (STT 결과)")

class AnalyzeResult(BaseModel):
    """면접 분석 결과 모델"""
    id: str = Field(..., description="고유 ID (UUID)")
    candidate_name: str = Field(..., description="지원자 이름")
    position: str = Field(..., description="지원 직무")
    summary: str = Field(..., description="평가 요약")
    strengths: str = Field(..., description="강점")
    weaknesses: str = Field(..., description="약점")
    
class ErrorResponse(BaseModel):
    """에러 응답 모델"""
    error: str = Field(..., description="에러 메시지")
    detail: Optional[str] = Field(None, description="상세 에러 정보") 