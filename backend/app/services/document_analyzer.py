from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient
from langchain_openai import AzureChatOpenAI
import os
import time
from ..config import settings

# settings에서 환경변수를 가져옴 (config.py에서 이미 로드됨)

class DocumentAnalyzer:
    def __init__(self):
        # Azure AI Search 기본 설정
        self.search_service_name = settings.azure_ai_search_service_name
        self.search_endpoint = f"https://{self.search_service_name}.search.windows.net"
        self.search_credential = AzureKeyCredential(settings.azure_ai_search_api_key)
        
        # 동적으로 인덱스 이름 찾기
        self.index_name = self._get_active_index_name()
        
        # Azure AI Search 클라이언트 설정
        self.search_client = SearchClient(
            endpoint=self.search_endpoint,
            index_name=self.index_name,
            credential=self.search_credential
        )
        
        # Azure Blob Storage 클라이언트 설정
        if settings.azure_storage_account_name and settings.azure_storage_account_key:
            self.blob_service_client = BlobServiceClient(
                account_url=f"https://{settings.azure_storage_account_name}.blob.core.windows.net",
                credential=settings.azure_storage_account_key
            )
        else:
            print("⚠️ Azure Storage 환경변수가 설정되지 않았습니다. 파일 업로드 기능을 사용할 수 없습니다.")
            self.blob_service_client = None
        
        self.container_name = settings.azure_storage_container_name
        
        # Azure OpenAI LLM 설정
        self.llm = AzureChatOpenAI(
            model=settings.azure_openai_deployment_name,
            temperature=0,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint,
            azure_deployment=settings.azure_openai_deployment_name,
        )
    
    def _get_active_index_name(self) -> str:
        """
        동적으로 활성 인덱스 이름 찾기
        'rag-'로 시작하는 인덱스 중 가장 최신 것을 반환
        """
        try:
            # SearchIndexClient로 인덱스 목록 조회
            index_client = SearchIndexClient(
                endpoint=self.search_endpoint,
                credential=self.search_credential
            )
            
            # 모든 인덱스 조회
            indexes = list(index_client.list_indexes())
            
            # 'rag-'로 시작하는 인덱스들 필터링
            rag_indexes = [idx.name for idx in indexes if idx.name.startswith('rag-')]
            
            if rag_indexes:
                # 가장 최신 인덱스 반환 (이름 기준 정렬)
                latest_index = sorted(rag_indexes, reverse=True)[0]
                print(f"✅ 자동 발견된 인덱스: {latest_index}")
                return latest_index
            else:
                # 기본 인덱스 이름 반환
                fallback_index = "rag-1751935906958"
                print(f"⚠️ rag- 인덱스를 찾을 수 없어서 기본값 사용: {fallback_index}")
                return fallback_index
                
        except Exception as e:
            # 오류 시 기본 인덱스 이름 사용
            fallback_index = "rag-1751935906958"
            print(f"❌ 인덱스 조회 오류, 기본값 사용: {fallback_index} (오류: {str(e)})")
            return fallback_index
    
    def upload_file_to_storage(self, file_content: bytes, filename: str) -> dict:
        """파일을 Azure Blob Storage에 업로드"""
        try:
            if self.blob_service_client is None:
                return {
                    "status": "error",
                    "message": "Azure Storage가 설정되지 않았습니다."
                }
            
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=filename
            )
            
            # 파일 업로드
            blob_client.upload_blob(file_content, overwrite=True)
            
            return {
                "status": "success",
                "message": f"파일 '{filename}'이 성공적으로 업로드되었습니다.",
                "filename": filename
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"파일 업로드 중 오류 발생: {str(e)}"
            }
    
    def upload_resume(self, file_content: bytes, filename: str) -> dict:
        """이력서 파일 업로드"""
        # 이력서 파일명 앞에 prefix 추가
        resume_filename = f"resume_{filename}"
        return self.upload_file_to_storage(file_content, resume_filename)
    
    def upload_job_posting(self, file_content: bytes, filename: str) -> dict:
        """채용공고 파일 업로드"""
        # 채용공고 파일명 앞에 prefix 추가
        job_filename = f"job_{filename}"
        return self.upload_file_to_storage(file_content, job_filename)
    
    def read_resume_file(self, filename: str) -> str:
        """이력서 파일 읽기 (AI Search에서)"""
        try:
            # resume_ prefix가 없으면 추가
            if not filename.startswith("resume_"):
                filename = f"resume_{filename}"
            
            print(f"🔍 이력서 파일 검색: {filename}")
            
            # 먼저 모든 문서를 검색해서 어떤 파일들이 있는지 확인
            all_results = self.search_client.search(
                search_text="*",
                top=10,
                select=["metadata_storage_name", "content", "chunk"]
            )
            
            print("📋 AI Search에서 찾은 파일들:")
            for result in all_results:
                storage_name = result.get("metadata_storage_name", "")
                print(f"  - {storage_name}")
            
            # 정확한 파일명으로 검색
            results = self.search_client.search(
                search_text=f"metadata_storage_name:{filename}",
                top=1,
                select=["content", "chunk", "metadata_storage_name"]
            )
            
            results_list = list(results)
            print(f"🔍 '{filename}' 검색 결과: {len(results_list)}개")
            
            for result in results_list:
                content = result.get("content", "") or result.get("chunk", "")
                storage_name = result.get("metadata_storage_name", "")
                print(f"  - 파일: {storage_name}, 내용 길이: {len(content)}자")
                if content:
                    return content
            
            # 파일명 부분 매칭으로 재시도
            print(f"🔍 부분 매칭으로 재시도: {filename}")
            results = self.search_client.search(
                search_text=filename,
                top=5,
                select=["content", "chunk", "metadata_storage_name"]
            )
            
            for result in results:
                storage_name = result.get("metadata_storage_name", "")
                if filename in storage_name:
                    content = result.get("content", "") or result.get("chunk", "")
                    print(f"  ✅ 부분 매칭 성공: {storage_name}")
                    if content:
                        return content
            
            return f"이력서 파일 '{filename}'을 찾을 수 없습니다. (AI Search 인덱싱 대기 중일 수 있습니다)"
        except Exception as e:
            print(f"❌ 이력서 파일 읽기 오류: {str(e)}")
            return f"이력서 파일 읽기 오류: {str(e)}"
    
    def read_job_posting_file(self, filename: str) -> str:
        """채용공고 파일 읽기 (AI Search에서)"""
        try:
            # job_ prefix가 없으면 추가
            if not filename.startswith("job_"):
                filename = f"job_{filename}"
            
            print(f"🔍 채용공고 파일 검색: {filename}")
            
            # 정확한 파일명으로 검색
            results = self.search_client.search(
                search_text=f"metadata_storage_name:{filename}",
                top=1,
                select=["content", "chunk", "metadata_storage_name"]
            )
            
            results_list = list(results)
            print(f"🔍 '{filename}' 검색 결과: {len(results_list)}개")
            
            for result in results_list:
                content = result.get("content", "") or result.get("chunk", "")
                storage_name = result.get("metadata_storage_name", "")
                print(f"  - 파일: {storage_name}, 내용 길이: {len(content)}자")
                if content:
                    return content
            
            # 파일명 부분 매칭으로 재시도
            print(f"🔍 부분 매칭으로 재시도: {filename}")
            results = self.search_client.search(
                search_text=filename,
                top=5,
                select=["content", "chunk", "metadata_storage_name"]
            )
            
            for result in results:
                storage_name = result.get("metadata_storage_name", "")
                if filename in storage_name:
                    content = result.get("content", "") or result.get("chunk", "")
                    print(f"  ✅ 부분 매칭 성공: {storage_name}")
                    if content:
                        return content
            
            return f"채용공고 파일 '{filename}'을 찾을 수 없습니다. (AI Search 인덱싱 대기 중일 수 있습니다)"
        except Exception as e:
            print(f"❌ 채용공고 파일 읽기 오류: {str(e)}")
            return f"채용공고 파일 읽기 오류: {str(e)}"
    
    def wait_for_indexing(self, filename: str, max_wait_time: int = 30) -> bool:
        """AI Search 인덱싱 완료 대기"""
        for _ in range(max_wait_time):
            try:
                results = self.search_client.search(
                    search_text=f"metadata_storage_name:{filename}",
                    top=1,
                    select=["content", "chunk"]
                )
                
                for result in results:
                    content = result.get("content", "") or result.get("chunk", "")
                    if content:
                        return True
                
                time.sleep(1)  # 1초 대기
            except:
                time.sleep(1)
        
        return False
    
    def analyze_match(self, resume_content: str, job_content: str) -> dict:
        """이력서-채용공고 매칭 분석"""
        try:
            # 파일 읽기 오류 확인
            if "오류" in resume_content or "찾을 수 없습니다" in resume_content:
                return {
                    "status": "error",
                    "message": f"이력서 파일 오류: {resume_content}"
                }
            
            if "오류" in job_content or "찾을 수 없습니다" in job_content:
                return {
                    "status": "error",
                    "message": f"채용공고 파일 오류: {job_content}"
                }
            
            # 내용이 너무 짧으면 오류로 처리
            if len(resume_content.strip()) < 50:
                return {
                    "status": "error",
                    "message": f"이력서 내용이 너무 짧습니다: {len(resume_content)}자"
                }
            
            if len(job_content.strip()) < 50:
                return {
                    "status": "error",
                    "message": f"채용공고 내용이 너무 짧습니다: {len(job_content)}자"
                }
            
            print(f"📊 분석 시작 - 이력서: {len(resume_content)}자, 채용공고: {len(job_content)}자")
            
            prompt = f"""
당신은 전문 채용 컨설턴트입니다. 다음 채용공고와 지원자 이력서를 분석하여 매칭도를 평가해주세요.

**채용공고:**
{job_content}

**지원자 이력서:**
{resume_content}

아래 형식으로 정리해주세요:

## 📊 종합 평가
- 전반적 적합도: XX/100점 (한줄 요약)
- 기술 스택 매칭: XX/100점 (핵심 매칭/부족 기술)
- 경력 충족도: XX/100점 (요구사항 충족 여부)

## ✅ 주요 강점
1. [구체적 강점 1]
2. [구체적 강점 2]
3. [구체적 강점 3]

## ⚠️ 우려 사항
1. [구체적 우려점 1]
2. [구체적 우려점 2]
3. [구체적 우려점 3]

## 💬 추천 면접 질문 5가지
1. [기술 관련 질문]
2. [프로젝트 경험 질문]
3. [문제 해결 질문]
4. [협업/소통 질문]
5. [성장 가능성 질문]
"""
            
            result = self.llm.invoke(prompt)
            
            return {
                "status": "success",
                "analysis": result.content
            }
            
        except Exception as e:
            print(f"❌ 분석 중 오류: {str(e)}")
            return {
                "status": "error",
                "message": f"분석 중 오류 발생: {str(e)}"
            }

    def get_blob_files_list(self) -> dict:
        """Azure Blob Storage에서 파일 목록 조회"""
        try:
            if self.blob_service_client is None:
                return {
                    "status": "error",
                    "message": "Azure Storage가 설정되지 않았습니다."
                }
            
            # 컨테이너의 모든 blob 목록 조회
            blob_list = self.blob_service_client.get_container_client(
                self.container_name
            ).list_blobs()
            
            resume_files = []
            job_files = []
            
            for blob in blob_list:
                if blob.name.startswith("resume_"):
                    resume_files.append({
                        "name": blob.name,
                        "display_name": blob.name.replace("resume_", ""),
                        "size": blob.size,
                        "last_modified": blob.last_modified.isoformat() if blob.last_modified else None
                    })
                elif blob.name.startswith("job_"):
                    job_files.append({
                        "name": blob.name,
                        "display_name": blob.name.replace("job_", ""),
                        "size": blob.size,
                        "last_modified": blob.last_modified.isoformat() if blob.last_modified else None
                    })
            
            # 최신 파일 순으로 정렬
            resume_files.sort(key=lambda x: x['last_modified'] or '', reverse=True)
            job_files.sort(key=lambda x: x['last_modified'] or '', reverse=True)
            
            return {
                "status": "success",
                "resume_files": resume_files,
                "job_files": job_files,
                "total_files": len(resume_files) + len(job_files)
            }
            
        except Exception as e:
            print(f"❌ Blob 파일 목록 조회 오류: {str(e)}")
            return {
                "status": "error",
                "message": f"파일 목록 조회 중 오류 발생: {str(e)}"
            }

# 전역 인스턴스 생성
document_analyzer = DocumentAnalyzer()

# 파일 업로드 함수들
def upload_resume_file(file_content: bytes, filename: str) -> dict:
    """이력서 파일 업로드"""
    return document_analyzer.upload_resume(file_content, filename)

def upload_job_posting_file(file_content: bytes, filename: str) -> dict:
    """채용공고 파일 업로드"""
    return document_analyzer.upload_job_posting(file_content, filename)

# 파일 읽기 함수들
def read_resume(filename: str) -> str:
    """이력서 파일 읽기"""
    return document_analyzer.read_resume_file(filename)

def read_job_posting(filename: str) -> str:
    """채용공고 파일 읽기"""
    return document_analyzer.read_job_posting_file(filename)

# 종합 분석 함수
def analyze_candidate_match(resume_file: str, job_file: str) -> dict:
    """이력서-채용공고 종합 분석"""
    resume_content = read_resume(resume_file)
    job_content = read_job_posting(job_file)
    return document_analyzer.analyze_match(resume_content, job_content)

# 인덱싱 대기 함수
def wait_for_file_indexing(filename: str, max_wait_time: int = 30) -> bool:
    """AI Search 인덱싱 완료 대기"""
    return document_analyzer.wait_for_indexing(filename, max_wait_time) 

# 파일 목록 조회 함수
def get_storage_files_list() -> dict:
    """Azure Blob Storage 파일 목록 조회"""
    return document_analyzer.get_blob_files_list() 