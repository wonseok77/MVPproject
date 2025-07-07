# MVPproject

## 프로젝트 개요
이 프로젝트는 Azure Computer Vision API와 OpenAI API를 활용한 이미지 분석 및 면접 평가 시스템입니다.

## 기능
- **Computer Vision**: Azure Computer Vision API를 사용한 이미지 분석
- **Object Detection**: 객체 감지 및 바운딩 박스 표시
- **OCR**: 이미지 내 텍스트 추출
- **Interview Analysis**: 면접 평가 보조 시스템
- **RAG Application**: 검색 강화 생성 애플리케이션
- **FastAPI Backend**: 면접 분석 및 평가 API 서버 (NEW!)
  - Azure OpenAI GPT-4o 기반 면접 분석
  - ChromaDB 벡터 저장소 활용
  - React 프론트엔드와 API 통신

## 설치 및 설정

### 1. Python 환경 설정
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정
1. `env_example.txt` 파일을 참조하여 `.env` 파일을 생성하세요
2. 각 API 키와 엔드포인트를 실제 값으로 설정하세요

### 3. 필요한 API 키
- **Azure Computer Vision API**: Azure Portal에서 Computer Vision 리소스 생성
- **OpenAI API**: OpenAI 또는 Azure OpenAI 서비스 구독
- **Azure Search**: RAG 기능을 위한 Azure Cognitive Search 서비스

## 사용법

### Computer Vision 애플리케이션
```bash
python python/01.computervision.py
python python/02.object_detection.py
```

### Streamlit 웹 애플리케이션
```bash
# 기본 앱
streamlit run python/app.py

# 면접 분석 시스템
streamlit run python/interview.py
```

### RAG 애플리케이션
```bash
python python/rag.app.py
```

### FastAPI 백엔드 서버
```bash
cd backend
pip install -r requirements.txt
python run.py
```

- **API 문서**: http://localhost:8000/docs
- **서버 주소**: http://localhost:8000

## 파일 구조
- `python/`: Python 스크립트 및 애플리케이션
- `UI/`: React/TypeScript 기반 프론트엔드
- `backend/`: FastAPI 백엔드 시스템
- `requirements.txt`: Python 패키지 의존성
- `env_example.txt`: 환경 변수 설정 예시

### 백엔드 구조
```
backend/
├── app/
│   ├── main.py              # FastAPI 애플리케이션
│   ├── config.py            # 환경변수 설정
│   ├── models.py            # Pydantic 모델
│   ├── routers/
│   │   └── analyze.py       # 면접 분석 API
│   └── services/
│       ├── azure_openai.py  # Azure OpenAI 서비스
│       └── chroma_store.py  # ChromaDB 저장소
├── requirements.txt         # 백엔드 의존성
├── env_config.txt          # 환경변수 설정 예시
├── run.py                  # 서버 실행 스크립트
└── README.md               # 백엔드 문서
```

## 주의사항
- API 키는 반드시 안전하게 보관하세요
- `.env` 파일은 git에 커밋하지 마세요
- 각 API 서비스의 사용량과 비용을 주의깊게 모니터링하세요 