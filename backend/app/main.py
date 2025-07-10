"""
FastAPI 메인 애플리케이션
"""
import logging
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routers import document_api, interview_api
from .config import settings

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="KT DS 면접 분석 시스템",
    description="신입사원 면접 분석 및 평가 보조 시스템",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정 (React 프론트엔드와 통신을 위해)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React 개발서버
        "http://localhost:5173",  # Vite 개발서버
        "*"  # Azure 배포 환경에서는 모든 origin 허용 (보안상 주의 필요)
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(document_api.router, prefix="/api")
app.include_router(interview_api.router, prefix="/api")

# 프론트엔드 정적 파일 서빙 설정
frontend_dist_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "UI", "dist")
if os.path.exists(frontend_dist_path):
    logger.info(f"프론트엔드 정적 파일 경로: {frontend_dist_path}")
    app.mount("/", StaticFiles(directory=frontend_dist_path, html=True), name="static")
else:
    logger.warning(f"프론트엔드 빌드 파일을 찾을 수 없음: {frontend_dist_path}")


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "KT DS 면접 분석 시스템 API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    try:
        return {
            "status": "healthy",
            "azure_openai_configured": bool(settings.azure_openai_api_key),
            "chroma_persist_dir": settings.chroma_persist_dir
        }
    except Exception as e:
        logger.error(f"헬스 체크 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail="서버 상태 확인 실패")

# 애플리케이션 시작시 실행되는 이벤트
@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작시 실행"""
    logger.info("KT DS 면접 분석 시스템 시작")
    logger.info(f"Azure OpenAI 설정: {bool(settings.azure_openai_api_key)}")
    logger.info(f"ChromaDB 디렉토리: {settings.chroma_persist_dir}")

# 애플리케이션 종료시 실행되는 이벤트
@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료시 실행"""
    logger.info("KT DS 면접 분석 시스템 종료")

# Force redeploy - ensure all backend files are properly deployed to Azure 