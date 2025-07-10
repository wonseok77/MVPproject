# KT DS 면접 분석 시스템

## 📋 프로젝트 개요

**KT DS 신입사원 면접 분석 및 평가 보조 Agent**는 AI를 활용하여 채용 담당자가 객관적이고 체계적인 면접 평가를 할 수 있도록 지원하는 웹 애플리케이션입니다.

### 🎯 주요 목적
- **문서 기반 분석**: 이력서와 채용공고를 비교하여 지원자 적합도 평가
- **음성 인식 및 분석**: 면접 녹음을 텍스트로 변환하고 AI가 면접 내용 분석
- **통합 평가**: 문서 분석 + 면접 분석을 결합한 종합적인 채용 결정 지원
- **결과 저장 및 관리**: 분석 결과를 체계적으로 저장하고 불러올 수 있는 기능

## 🤖 AI Agent System Prompt & Persona

### 📝 Agent Persona (에이전트 역할)
본 시스템의 AI 에이전트는 **전문 면접관이자 HR 컨설턴트**로 설계되어 있습니다.

#### 🎯 주요 역할
- **전문 면접관**: 다년간의 채용 경험을 바탕으로 한 객관적 평가
- **HR 컨설턴트**: 인재 개발과 조직 적합성 관점에서의 통찰력
- **데이터 분석가**: 정량적 지표와 정성적 평가의 균형잡힌 분석
- **멘토링 전문가**: 지원자의 성장 가능성과 발전 방향 제시

### 🔍 Agent System Prompt 구조

#### 1. 📊 다차원 평가 시스템
AI 에이전트는 **5가지 핵심 영역**에서 지원자를 평가합니다:

```
🎯 평가 영역 (각 100점 만점)
├── 의사소통 능력 (명확성, 논리성, 표현력)
├── 기술적 역량 (전문 지식, 경험, 문제해결)
├── 협업 및 팀워크 (소통, 협력, 리더십)
├── 성장 가능성 (학습 의지, 적응력, 발전성)
└── 직무 적합성 (직무 이해도, 경험 매칭)
```

#### 2. 🎨 분석 프레임워크
```
📋 종합 분석 구조
├── ✅ 주요 강점 (3가지 구체적 강점 + 상세 설명)
├── ⚠️ 개선 필요 사항 (3가지 개선점 + 구체적 방안)
├── 💬 핵심 답변 분석 (인상적 답변 vs 아쉬운 답변)
├── 🎖️ 최종 채용 권고 (강력추천/조건부추천/보류/불합격)
└── 📝 추가 검증 포인트 (레퍼런스, 실무테스트, 온보딩)
```

#### 3. 🏆 채용 결정 지원 체계
```
🎖️ 4단계 채용 권고 시스템
├── 강력 추천 (90점 이상) - 즉시 채용 권고
├── 조건부 추천 (70-89점) - 특정 조건 하 채용 권고
├── 보류 (50-69점) - 추가 검증 후 재평가
└── 불합격 (50점 미만) - 현 시점 부적합 판정
```

### 🧠 Agent Intelligence Features

#### 💡 고급 분석 능력
- **맥락 이해**: 단순 키워드 매칭이 아닌 문맥적 의미 파악
- **패턴 인식**: 우수 인재의 공통 특성 및 성공 패턴 분석
- **예측 분석**: 조직 내 성공 가능성 및 적응도 예측
- **비교 분석**: 채용공고 요구사항과 지원자 역량의 정밀 매칭

#### 🔬 분석 깊이 제어
```
⚡ 빠른 분석 모드 (10초)
├── 기본 적합도 평가
├── 핵심 강점/약점 식별
└── 간단한 채용 권고

🔄 정밀 분석 모드 (30초)
├── 심층 역량 분석
├── 성장 가능성 평가
├── 조직 문화 적합성 분석
├── 구체적 개선 방안 제시
└── 상세한 후속 질문 제안
```

#### 🎯 맞춤형 평가 기준
- **직무별 가중치**: 개발자, 기획자, 디자이너 등 직무 특성 반영
- **경력별 기준**: 신입/경력/시니어 수준별 차별화된 평가
- **조직별 문화**: 기업 문화와 팀 특성에 맞는 인재상 적용

### 🎪 Agent Prompt Examples

#### 📄 문서 분석 프롬프트
```
당신은 전문 채용 컨설턴트입니다. 
이력서와 채용공고를 비교하여 지원자의 적합도를 평가해주세요.

분석 기준:
- 필수 요건 충족도
- 경력 및 기술 스택 매칭
- 성장 가능성 및 잠재력
- 조직 문화 적합성
```

#### 🎤 면접 분석 프롬프트
```
당신은 전문 면접관이자 HR 컨설턴트입니다. 
다음 면접 내용을 분석하여 지원자를 평가해주세요.

평가 영역:
- 의사소통 능력 (명확성, 논리성, 표현력)
- 기술적 역량 (전문 지식, 경험, 문제해결)
- 협업 및 팀워크 (소통, 협력, 리더십)
- 성장 가능성 (학습 의지, 적응력, 발전성)
- 직무 적합성 (직무 이해도, 경험 매칭)
```

### 🎮 Agent Interaction Flow

#### 🔄 2단계 분석 워크플로우
```
1단계: 문서 분석 📄
├── 이력서 파싱 및 구조화
├── 채용공고 요구사항 추출
├── 적합도 매칭 스코어링
└── 초기 평가 리포트 생성

2단계: 면접 분석 🎤
├── 음성 → 텍스트 변환 (STT)
├── 면접 내용 의미 분석
├── 5개 영역 정량 평가
└── 상세 피드백 생성

3단계: 통합 분석 🎯
├── 문서 + 면접 종합 평가
├── 최종 채용 권고 생성
├── 성장 로드맵 제시
└── 후속 액션 플랜 제안
```

### 🛡️ Agent Ethics & Guidelines

#### 🤝 공정성 원칙
- **편견 방지**: 성별, 나이, 출신 등 차별 요소 배제
- **객관성 유지**: 데이터 기반 정량 평가 + 정성적 통찰
- **투명성 보장**: 평가 근거와 개선 방안 명시
- **일관성 확보**: 동일한 기준으로 모든 지원자 평가

#### 📊 데이터 프라이버시
- **개인정보 보호**: 민감 정보 처리 시 암호화 적용
- **데이터 최소화**: 분석에 필요한 최소한의 정보만 활용
- **임시 저장**: 분석 후 불필요한 데이터 자동 삭제

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Web    │    │   FastAPI       │    │  Azure Cloud    │
│   Frontend      │◄──►│   Backend       │◄──►│   Services      │
│                 │    │                 │    │                 │
│ • 파일 업로드    │    │ • 문서 분석      │    │ • OpenAI GPT-4o │
│ • 분석 결과 표시 │    │ • STT 처리      │    │ • Blob Storage  │
│ • 결과 저장/로드 │    │ • 통합 분석      │    │ • AI Search     │
│                 │    │ • JSON 저장소    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ 기술 스택

### Frontend
- **React 18** + **TypeScript** - 모던 웹 애플리케이션 프레임워크
- **Vite** - 빠른 개발 서버 및 빌드 도구
- **Tailwind CSS** - 유틸리티 기반 CSS 프레임워크
- **Lucide React** - 아이콘 라이브러리

### Backend
- **FastAPI** - 고성능 Python 웹 프레임워크
- **Python 3.13** - 최신 Python 언어
- **Pydantic** - 데이터 검증 및 직렬화
- **Uvicorn** - ASGI 서버

### AI & Cloud Services
- **Azure OpenAI GPT-4o** - 문서 분석 및 평가
- **Azure OpenAI GPT-4o-transcribe** - 음성-텍스트 변환 (STT)
- **Azure Blob Storage** - 파일 저장소
- **Azure AI Search** - 문서 검색 및 인덱싱

### Development Tools
- **Docker** - 컨테이너화 (옵션)
- **ESLint** + **TypeScript** - 코드 품질 관리

## 🚀 주요 기능

### 1. 📄 문서 분석
- **이력서 업로드**: PDF, DOC, DOCX 형식 지원
- **채용공고 업로드**: 다양한 문서 형식 지원
- **자동 텍스트 추출**: Azure AI Search를 통한 고급 문서 파싱
- **적합도 분석**: AI 기반 이력서-채용공고 매칭 점수 계산

### 2. 🎤 음성 인식 및 면접 분석
- **실시간 STT**: Azure OpenAI GPT-4o-transcribe 엔진 사용
- **다양한 음성 형식 지원**: MP3, WAV, M4A
- **면접 내용 분석**: AI 기반 면접 평가 (의사소통, 기술역량, 협업능력 등)
- **기존 파일 처리**: 저장된 면접 녹음 파일 STT 처리 지원

### 3. 🎯 통합 분석 및 평가
- **2단계 분석 시스템**: 문서 분석 → 면접 분석 → 종합 평가
- **종합 점수 계산**: 다차원 평가 지표 기반 최종 점수
- **채용 추천**: 강력추천/조건부추천/보류/불합격 결정 지원
- **추가 질문 제안**: 맞춤형 후속 면접 질문 제공

### 4. 💾 결과 저장 및 관리
- **분석 결과 저장**: JSON 형태로 체계적 저장
- **히스토리 관리**: 과거 분석 결과 목록 조회
- **빠른 불러오기**: 저장된 결과 즉시 복원
- **파일 기반 저장**: Azure Blob Storage 활용

### 5. ⚡ 성능 최적화
- **빠른 분석 모드**: 10초 이내 결과 제공
- **정밀 분석 모드**: 30초 완전 분석 (깊은 의미 파악)
- **스마트 인덱싱**: 자동 인덱스 감지 및 업데이트
- **캐싱 시스템**: 중복 분석 방지

## 🔌 API 엔드포인트

### 📄 문서 분석 API (`/api/document`)

#### ✅ 활성 엔드포인트
- `POST /upload-resume` - 이력서 파일 업로드
- `POST /upload-job` - 채용공고 파일 업로드
- `POST /analyze-files` - 업로드된 파일들 분석
- `POST /upload-and-analyze` - 업로드+분석 한번에 (정밀모드)
- `POST /upload-and-analyze-fast` - 업로드+분석 한번에 (고속모드)
- `GET /files-list` - 저장된 파일 목록 조회
- `POST /integrated-analysis` - 2단계 통합 분석
- `POST /save-analysis-result` - 분석 결과 저장
- `GET /get-saved-results` - 저장된 결과 목록 조회
- `GET /load-analysis-result/{filename}` - 특정 결과 불러오기
- `DELETE /delete-analysis-result/{filename}` - 결과 삭제

#### ⚠️ 비활성/개발용 엔드포인트
- `POST /upload-both` - 동시 업로드 (사용 안함)
- `POST /analyze-text` - 직접 텍스트 분석 (사용 안함)
- `GET /debug-index` - 인덱스 디버깅 (개발자용)
- `POST /run-indexer` - 인덱서 수동 실행 (개발자용)
- `GET /indexer-status` - 인덱서 상태 확인 (개발자용)

### 🎤 면접 분석 API (`/api/interview`)

#### ✅ 활성 엔드포인트
- `POST /upload-and-transcribe` - 면접 녹음 업로드+STT 한번에
- `POST /quick-analysis` - 기존 STT 결과로 빠른 분석
- `GET /audio-files` - 저장된 면접 녹음 파일 목록
- `POST /transcribe-existing-file` - 기존 파일 STT 처리

#### ⚠️ 비활성 엔드포인트
- `POST /upload-audio` - 개별 업로드 (사용 안함)
- `POST /transcribe` - 개별 STT (사용 안함)
- `POST /analyze` - 개별 분석 (사용 안함)
- `POST /full-analysis` - 전체 분석 (사용 안함)

## 🗃️ Azure Blob Storage 파일 저장 구조

### 컨테이너 구성
```
user04containereastus2/
├── resume_[파일명]           # 이력서 파일
├── job_[파일명]              # 채용공고 파일
├── interview_[파일명]        # 면접 녹음 파일
└── analysis_[타임스탬프].json # 분석 결과 파일
```

### 파일 명명 규칙
- **이력서**: `resume_홍길동_이력서.pdf`
- **채용공고**: `job_백엔드개발자_채용공고.pdf`
- **면접 녹음**: `interview_홍길동_면접녹음.m4a`
- **분석 결과**: `analysis_20250709_143022.json`

### 지원 파일 형식
- **문서**: PDF, DOC, DOCX
- **음성**: MP3, WAV, M4A (iPhone 녹음 포함)
- **결과**: JSON (구조화된 데이터)

## 📊 면접 결과 저장 시스템

### 저장 데이터 구조
```json
{
  "metadata": {
    "timestamp": "2025-07-09T14:30:22",
    "resume_file": "resume_홍길동_이력서.pdf",
    "job_file": "job_백엔드개발자_채용공고.pdf",
    "analysis_mode": "integrated"
  },
  "results": {
    "document_analysis": "문서 분석 결과 텍스트...",
    "interview_stt": "면접 STT 변환 텍스트...",
    "integrated_analysis": "최종 종합 분석 결과..."
  },
  "scores": {
    "document_match": 85,
    "interview_score": 78,
    "overall_score": 82
  }
}
```

### 저장 프로세스
1. **자동 저장**: 분석 완료 시 타임스탬프 기반 파일명으로 저장
2. **메타데이터 포함**: 분석 시점, 사용 파일, 분석 모드 정보 저장
3. **빠른 복원**: 저장된 결과를 UI에서 즉시 불러오기 가능
4. **히스토리 관리**: 과거 분석 결과 목록 제공

## 📁 프로젝트 구조

```
MVPproject/
├── README.md                 # 프로젝트 설명서
├── requirements.txt          # Python 패키지 의존성
│
├── backend/                  # FastAPI 백엔드
│   ├── app/
│   │   ├── main.py          # FastAPI 애플리케이션 진입점
│   │   ├── config.py        # 환경변수 및 설정 관리
│   │   ├── models.py        # Pydantic 데이터 모델
│   │   ├── routers/
│   │   │   ├── document_api.py  # 문서 분석 API
│   │   │   └── interview_api.py # 면접 분석 API
│   │   └── services/
│   │       ├── document_analyzer.py # 문서 분석 서비스
│   │       ├── speech_service.py    # 음성 처리 서비스
│   │       ├── rag.py              # RAG 시스템
│   │       └── chroma_store.py     # JSON 임시 저장소
│   ├── run.py              # 서버 실행 스크립트
│   └── README.md           # 백엔드 문서
│
├── UI/                      # React 프론트엔드
│   ├── public/
│   │   └── ktds.png        # KT DS 로고 (favicon)
│   ├── src/
│   │   ├── components/
│   │   │   ├── App.tsx         # 메인 애플리케이션
│   │   │   ├── Sidebar.tsx     # 파일 업로드 사이드바
│   │   │   ├── MainContent.tsx # 분석 결과 표시
│   │   │   ├── ResultSidebar.tsx # 결과 저장/불러오기
│   │   │   └── FileUploader.tsx  # 파일 업로드 컴포넌트
│   │   ├── services/
│   │   │   └── api.ts          # 백엔드 API 통신
│   │   ├── main.tsx            # React 진입점
│   │   └── index.css           # 글로벌 스타일
│   ├── index.html              # HTML 템플릿
│   ├── package.json            # Node.js 의존성
│   ├── vite.config.ts         # Vite 설정
│   └── tailwind.config.js     # Tailwind CSS 설정
│
└── python/                  # 레거시 Python 스크립트들
    ├── 01.computervision.py     # Computer Vision 예제
    ├── 02.object_detection.py   # 객체 감지 예제
    ├── app.py                  # Streamlit 앱
    ├── interview.py            # 면접 분석 Streamlit
    └── rag.app.py             # RAG 애플리케이션
```

## ⚙️ 설치 및 실행

### 1. 전체 시스템 요구사항
- **Python 3.13+**
- **Node.js 18+**
- **Azure 구독** (OpenAI, Blob Storage, AI Search)

### 2. 환경 변수 설정
`.env` 파일을 프로젝트 루트에 생성:
```bash
# Azure OpenAI 설정
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-eastus2
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# Azure OpenAI Transcription 설정 (STT용)
AZUREOPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZUREOPENAI_KEY=your_transcription_key
AZUREOPENAI_API_VERSION=2025-01-01-preview
AZUREOPENAI_TRANSCRIPTION_MODEL=gpt-4o-transcribe-eastus2

# Azure Storage 설정
AZURE_STORAGE_ACCOUNT_NAME=your_storage_account
AZURE_STORAGE_ACCOUNT_KEY=your_storage_key
AZURE_STORAGE_CONTAINER_NAME=your_container

# Azure AI Search 설정
AZURE_AI_SEARCH_SERVICE_NAME=your_search_service
AZURE_AI_SEARCH_API_KEY=your_search_key
AZURE_AI_SEARCH_INDEX_NAME=your_index_name
```

### 3. 백엔드 실행
```bash
# 가상환경 생성 및 활성화
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# 패키지 설치
pip install -r requirements.txt

# 서버 실행
cd backend
python run.py
```

### 4. 프론트엔드 실행
```bash
# Node.js 패키지 설치
cd UI
npm install

# 개발 서버 실행
npm run dev
```

### 5. 접속 주소
- **웹 애플리케이션**: http://localhost:5173
- **백엔드 API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs

## 🎮 사용 가이드

### 기본 워크플로우

#### 1단계: 문서 업로드 및 분석
1. **파일 업로드**: 이력서와 채용공고를 업로드
2. **분석 모드 선택**: 빠른 분석(10초) 또는 정밀 분석(30초)
3. **문서 분석 실행**: "⚡ 빠른 분석" 또는 "🔄 정밀 분석" 버튼 클릭
4. **결과 확인**: 문서 분석 결과에서 적합도 및 상세 평가 확인

#### 2단계: 면접 분석
1. **녹음 파일 업로드**: 면접 녹음 파일(MP3, WAV, M4A) 업로드
2. **자동 STT 처리**: 업로드와 동시에 음성-텍스트 변환 진행
3. **STT 결과 확인**: "면접 STT 결과" 섹션에서 변환된 텍스트 확인

#### 3단계: 종합 평가
1. **통합 분석**: "🎯 2단계: 최종 종합 평가" 버튼 클릭
2. **최종 결과 확인**: 문서 + 면접 종합 분석 결과 확인
3. **채용 결정 지원**: 강점, 우려사항, 추천 질문, 채용 권고 확인

#### 4단계: 결과 저장 및 관리
1. **결과 저장**: 오른쪽 사이드바에서 "분석 결과 저장" 클릭
2. **히스토리 조회**: "저장된 결과 목록" 에서 과거 분석 결과 확인
3. **빠른 복원**: 저장된 결과를 클릭하여 즉시 불러오기

### 기존 파일 활용
1. **기존 파일 목록 보기**: 사이드바에서 "기존 파일 목록 보기" 클릭
2. **파일 선택**: 드롭다운에서 이력서, 채용공고, 면접 녹음 파일 선택
3. **전체 분석**: "🎯 전체 분석 (문서+면접)" 버튼으로 한번에 처리

## 🔧 고급 기능

### 성능 최적화
- **스마트 인덱싱**: Azure AI Search 인덱스 자동 감지 및 업데이트
- **캐싱 시스템**: 동일 파일 중복 분석 방지
- **백그라운드 처리**: 긴 작업을 백그라운드에서 비동기 처리

### 개발자 기능
- **API 문서**: http://localhost:8000/docs 에서 전체 API 스펙 확인
- **디버깅 도구**: 인덱스 상태 확인, 인덱서 수동 실행 가능
- **로깅 시스템**: 상세한 처리 과정 로그 제공

## 🔐 보안 및 주의사항

### 데이터 보안
- **API 키 보호**: 환경 변수 사용으로 키 노출 방지
- **CORS 설정**: 특정 도메인만 접근 허용
- **파일 검증**: 업로드 파일 형식 및 크기 제한

### 사용량 관리
- **Azure OpenAI**: 토큰 사용량 모니터링 필요
- **Storage 비용**: Blob Storage 사용량 주의
- **AI Search**: 검색 요청 수 관리

## 🐛 문제 해결

### 자주 발생하는 문제

#### STT 404 오류
- **증상**: "Resource not found" 오류
- **해결**: Azure Portal에서 deployment 이름과 API 버전 확인

#### 파일 업로드 실패
- **증상**: 파일 업로드 시 오류
- **해결**: Azure Storage 계정 키와 컨테이너 이름 확인

#### 분석 결과 없음
- **증상**: 분석 완료 후 결과가 표시되지 않음
- **해결**: ChromaDB 디렉토리 권한 및 인덱싱 상태 확인

### 로그 확인
- **백엔드 로그**: 터미널에서 실시간 로그 확인
- **브라우저 콘솔**: F12 개발자 도구로 프론트엔드 오류 확인

## 📞 지원 및 문의

### 개발팀 연락처
- **개발자**: Claude Assistant (Anthropic)
- **프로젝트**: KT DS MVP 프로젝트
- **버전**: 1.0.0

### 업데이트 내역
- **v1.0.0** (2025-07-09): 초기 출시
  - 문서 분석 시스템
  - 면접 STT 및 분석 시스템
  - 통합 분석 기능
  - 결과 저장 및 관리 시스템

---

**KT DS 면접 분석 시스템**으로 더욱 객관적이고 효율적인 채용 프로세스를 구축하세요! 🚀 