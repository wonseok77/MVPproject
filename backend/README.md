# KT DS 면접 분석 시스템 백엔드

## 개요
KT DS 신입사원 면접 분석 및 평가 보조 시스템의 FastAPI 백엔드입니다.

## 기능
- **면접 분석 API**: Azure OpenAI (GPT-4o)를 활용한 면접 분석
- **ChromaDB 저장**: 분석 결과 벡터 저장소에 저장
- **검색 기능**: 저장된 분석 결과 검색 및 조회
- **CORS 지원**: React 프론트엔드와 통신

## 설치 및 설정

### 1. 의존성 설치
```bash
cd backend
pip install -r requirements.txt
```

### 2. Azure 서비스 설정
시스템은 Azure 클라우드 서비스와 연동되어 동작합니다:

- **Azure OpenAI**: GPT-4o 모델을 활용한 지능형 분석
- **Azure Blob Storage**: 파일 저장 및 관리
- **Azure AI Search**: 문서 인덱싱 및 검색
- **Azure Web App**: 프로덕션 환경 배포

### 3. 필요한 Azure 서비스
- **Azure OpenAI**: GPT-4o 모델 배포 필요
- **ChromaDB**: 로컬 저장소 자동 생성

## 실행 방법

### 방법 1: run.py 사용
```bash
python run.py
```

### 방법 2: uvicorn 직접 실행
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 방법 3: FastAPI 개발 서버
```bash
cd backend
python -m uvicorn app.main:app --reload
```

## API 엔드포인트

### 기본 정보
- **서버 주소**: `http://localhost:8000`
- **API 문서**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### 주요 엔드포인트

#### 1. 면접 분석
```
POST /analyze/interview
```

**요청 데이터:**
```json
{
  "candidate_name": "김지훈",
  "position": "백엔드 개발자",
  "resume_text": "이력서 내용...",
  "job_posting_text": "채용공고 내용...",
  "interview_text": "면접 내용 (STT 결과)..."
}
```

**응답 데이터:**
```json
{
  "id": "uuid-generated-id",
  "candidate_name": "김지훈",
  "position": "백엔드 개발자",
  "summary": "평가 요약...",
  "strengths": "강점 분석...",
  "weaknesses": "약점 분석..."
}
```

#### 2. 분석 결과 조회
```
GET /analyze/result/{document_id}
```

#### 3. 분석 결과 검색
```
GET /analyze/search?query=검색어&limit=10
```

#### 4. 헬스 체크
```
GET /health
```

## 프로젝트 구조

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 애플리케이션
│   ├── config.py            # 환경변수 설정
│   ├── models.py            # Pydantic 모델
│   ├── routers/
│   │   ├── __init__.py
│   │   └── analyze.py       # 분석 API 라우터
│   └── services/
│       ├── __init__.py
│       ├── azure_openai.py  # Azure OpenAI 서비스
│       └── chroma_store.py  # ChromaDB 저장소
├── .env                     # 환경변수 (생성 필요)
├── requirements.txt         # 의존성 패키지
├── run.py                   # 서버 실행 스크립트
└── README.md               # 문서
```

## 개발 가이드

### 로그 확인
서버 실행 시 콘솔에서 로그를 확인할 수 있습니다:
```
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 테스트
API 테스트는 다음 방법으로 수행할 수 있습니다:
1. **Swagger UI**: `http://localhost:8000/docs`
2. **curl 명령어**:
```bash
curl -X POST "http://localhost:8000/analyze/interview" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_name": "테스트",
    "position": "개발자",
    "resume_text": "이력서 내용",
    "job_posting_text": "채용공고 내용",
    "interview_text": "면접 내용"
  }'
```

### 디버깅
- **로그 레벨**: INFO 레벨로 설정되어 있음
- **리로드**: 개발 모드에서 파일 변경 시 자동 리로드
- **오류 추적**: 상세한 오류 메시지와 스택 트레이스 제공

## 주의사항
- **클라우드 보안**: Azure 플랫폼 보안 정책 적용
- **CORS 설정**: 프로덕션 환경에 맞게 오리진 설정
- **포트 설정**: 기본 포트 8000, Azure Web App에서 동적 할당
- **ChromaDB**: 로컬 디렉토리에 데이터 저장됨

## 문제 해결
- **모듈 임포트 오류**: `pip install -r requirements.txt` 실행
- **Azure OpenAI 오류**: Azure 서비스 연결 상태 확인
- **ChromaDB 오류**: 디렉토리 권한 및 공간 확인
- **배포 오류**: Azure Web App 로그 확인 