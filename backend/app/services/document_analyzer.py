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
                fallback_index = "rag-1752025961760"
                print(f"⚠️ rag- 인덱스를 찾을 수 없어서 기본값 사용: {fallback_index}")
                return fallback_index
                
        except Exception as e:
            # 오류 시 기본 인덱스 이름 사용
            fallback_index = "rag-1752025961760"
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
            
            # 인덱스 스키마 확인
            schema_info = self.get_index_schema()
            if schema_info["status"] == "error":
                return f"인덱스 스키마 조회 실패: {schema_info['message']}"
            
            available_fields = schema_info["fields"]
            print(f"📋 사용 가능한 필드들: {available_fields}")
            
            # 사용할 필드들 결정
            content_fields = []
            filename_field = None
            
            # 파일명을 위한 필드 찾기
            for field in ["title", "metadata_storage_name", "metadata_storage_path", "filename", "name"]:
                if field in available_fields:
                    filename_field = field
                    print(f"✅ 파일명 필드로 '{field}' 사용")
                    break
            
            # 컨텐츠를 위한 필드들 찾기
            for field in ["chunk", "content", "text", "body"]:
                if field in available_fields:
                    content_fields.append(field)
            
            print(f"✅ 컨텐츠 필드들: {content_fields}")
            
            if not filename_field:
                print("⚠️ 파일명 필드를 찾을 수 없어서 전체 검색으로 진행합니다")
                # 전체 검색으로 진행
                all_results = self.search_client.search(
                    search_text="*",
                    top=10,
                    select=content_fields
                )
                
                print("📋 AI Search에서 찾은 문서들:")
                doc_count = 0
                for result in all_results:
                    doc_count += 1
                    content = ""
                    for field in content_fields:
                        field_content = result.get(field, "")
                        if field_content and len(field_content) > len(content):
                            content = field_content
                    print(f"  - 문서 {doc_count}: 내용 길이 {len(content)}자")
                    if filename.lower() in content.lower() and len(content) > 100:
                        print(f"  ✅ 파일명이 포함된 문서 발견!")
                        return content
                
                return f"이력서 파일 '{filename}'을 찾을 수 없습니다"
            
            # 파일명 필드가 있는 경우 정확한 검색
            select_fields = [filename_field] + content_fields
            
            # 먼저 모든 문서를 검색해서 어떤 파일들이 있는지 확인
            try:
                all_results = self.search_client.search(
                    search_text="*",
                    top=10,
                    select=select_fields
                )
                
                print("📋 AI Search에서 찾은 파일들:")
                for result in all_results:
                    storage_name = result.get(filename_field, "")
                    print(f"  - {storage_name}")
            except Exception as e:
                print(f"⚠️ 전체 문서 조회 오류: {str(e)}")
            
            # 다양한 검색 방식으로 시도
            search_queries = [
                f'"{filename}"',  # 정확한 매칭
                filename,         # 일반 검색
                filename.replace("resume_", "").replace("job_", ""),  # prefix 제거
                f"{filename_field}:{filename}",  # 필드 특정 검색
            ]
            
            for i, search_query in enumerate(search_queries):
                try:
                    print(f"🔍 검색 시도 {i+1}: '{search_query}'")
                    results = self.search_client.search(
                        search_text=search_query,
                        top=5,
                        select=select_fields
                    )
                    
                    results_list = list(results)
                    print(f"   → {len(results_list)}개 결과")
                    
                    for result in results_list:
                        storage_name = result.get(filename_field, "")
                        content = ""
                        for field in content_fields:
                            field_content = result.get(field, "")
                            if field_content and len(field_content) > len(content):
                                content = field_content
                        
                        print(f"  - 파일: {storage_name}")
                        print(f"    내용 길이: {len(content)}자")
                        
                        # 파일명 매칭 조건들
                        original_filename = filename.replace("resume_", "").replace("job_", "")
                        match_conditions = [
                            filename in storage_name,
                            storage_name in filename,
                            original_filename in storage_name,
                            any(word in storage_name for word in original_filename.split("_") if len(word) > 2)
                        ]
                        
                        if any(match_conditions) and content and len(content) > 50:
                            print(f"  ✅ 매칭 성공: {storage_name}")
                            return content
                            
                except Exception as e:
                    print(f"⚠️ 검색 시도 {i+1} 오류: {str(e)}")
            
            # 모든 문서를 검색해서 사용 가능한 파일 목록 표시
            print("📋 현재 인덱스에 있는 모든 파일:")
            try:
                all_results = self.search_client.search(
                    search_text="*",
                    top=10,
                    select=select_fields
                )
                
                available_files = []
                for result in all_results:
                    storage_name = result.get(filename_field, "")
                    if storage_name:
                        available_files.append(storage_name)
                        print(f"  - {storage_name}")
                
                if available_files:
                    suggestion_msg = f"\n💡 '{filename}' 파일을 찾을 수 없습니다.\n"
                    suggestion_msg += f"현재 사용 가능한 파일: {', '.join(available_files)}\n"
                    suggestion_msg += f"파일을 다시 업로드하거나 올바른 파일명을 확인해주세요."
                    return suggestion_msg
                else:
                    return f"인덱스에 문서가 없습니다. 파일을 업로드해주세요."
                        
            except Exception as e:
                print(f"⚠️ 전체 파일 목록 조회 오류: {str(e)}")
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
            
            # 인덱스 스키마 확인 (캐시된 결과 사용 가능)
            schema_info = self.get_index_schema()
            if schema_info["status"] == "error":
                return f"인덱스 스키마 조회 실패: {schema_info['message']}"
            
            available_fields = schema_info["fields"]
            
            # 사용할 필드들 결정
            content_fields = []
            filename_field = None
            
            # 파일명을 위한 필드 찾기
            for field in ["metadata_storage_name", "metadata_storage_path", "filename", "name", "title"]:
                if field in available_fields:
                    filename_field = field
                    break
            
            # 컨텐츠를 위한 필드들 찾기
            for field in ["content", "chunk", "text", "body"]:
                if field in available_fields:
                    content_fields.append(field)
            
            if not filename_field:
                print("⚠️ 파일명 필드를 찾을 수 없어서 전체 검색으로 진행합니다")
                # 전체 검색으로 진행
                all_results = self.search_client.search(
                    search_text="*",
                    top=10,
                    select=content_fields
                )
                
                for result in all_results:
                    content = ""
                    for field in content_fields:
                        field_content = result.get(field, "")
                        if field_content and len(field_content) > len(content):
                            content = field_content
                    if filename.lower() in content.lower() and len(content) > 100:
                        print(f"  ✅ 파일명이 포함된 문서 발견!")
                        return content
                
                return f"채용공고 파일 '{filename}'을 찾을 수 없습니다"
            
            # 파일명 필드가 있는 경우 정확한 검색
            select_fields = [filename_field] + content_fields
            
            # 정확한 파일명으로 검색
            try:
                results = self.search_client.search(
                    search_text=f"{filename_field}:{filename}",
                    top=1,
                    select=select_fields
                )
                
                results_list = list(results)
                print(f"🔍 '{filename}' 검색 결과: {len(results_list)}개")
                
                for result in results_list:
                    storage_name = result.get(filename_field, "")
                    content = ""
                    for field in content_fields:
                        field_content = result.get(field, "")
                        if field_content and len(field_content) > len(content):
                            content = field_content
                    
                    print(f"  - 파일: {storage_name}, 내용 길이: {len(content)}자")
                    if content:
                        return content
            except Exception as e:
                print(f"⚠️ 정확한 파일명 검색 오류: {str(e)}")
            
            # 파일명 부분 매칭으로 재시도
            print(f"🔍 부분 매칭으로 재시도: {filename}")
            try:
                results = self.search_client.search(
                    search_text=filename,
                    top=5,
                    select=select_fields
                )
                
                for result in results:
                    storage_name = result.get(filename_field, "")
                    if filename in storage_name:
                        content = ""
                        for field in content_fields:
                            field_content = result.get(field, "")
                            if field_content and len(field_content) > len(content):
                                content = field_content
                        
                        print(f"  ✅ 부분 매칭 성공: {storage_name}")
                        if content:
                            return content
            except Exception as e:
                print(f"⚠️ 부분 매칭 검색 오류: {str(e)}")
            
            return f"채용공고 파일 '{filename}'을 찾을 수 없습니다. (AI Search 인덱싱 대기 중일 수 있습니다)"
        except Exception as e:
            print(f"❌ 채용공고 파일 읽기 오류: {str(e)}")
            return f"채용공고 파일 읽기 오류: {str(e)}"
    
    def wait_for_indexing(self, filename: str, max_wait_time: int = 30) -> bool:
        """AI Search 인덱싱 완료 대기"""
        try:
            # 인덱스 스키마 확인
            schema_info = self.get_index_schema()
            if schema_info["status"] == "error":
                print(f"⚠️ 스키마 조회 실패, 기본 방식으로 대기: {schema_info['message']}")
                # 기본 방식으로 대기
                for _ in range(max_wait_time):
                    try:
                        results = self.search_client.search(
                            search_text=filename,
                            top=1
                        )
                        for result in results:
                            return True
                        time.sleep(1)
                    except:
                        time.sleep(1)
                return False
            
            available_fields = schema_info["fields"]
            
            # 파일명 필드와 컨텐츠 필드 찾기
            filename_field = None
            content_fields = []
            
            for field in ["metadata_storage_name", "metadata_storage_path", "filename", "name", "title"]:
                if field in available_fields:
                    filename_field = field
                    break
            
            for field in ["content", "chunk", "text", "body"]:
                if field in available_fields:
                    content_fields.append(field)
            
            if not filename_field or not content_fields:
                print(f"⚠️ 필요한 필드를 찾을 수 없어서 기본 검색으로 대기")
                # 기본 방식으로 대기
                for _ in range(max_wait_time):
                    try:
                        results = self.search_client.search(
                            search_text=filename,
                            top=1
                        )
                        for result in results:
                            return True
                        time.sleep(1)
                    except:
                        time.sleep(1)
                return False
            
            select_fields = [filename_field] + content_fields
            
            for i in range(max_wait_time):
                try:
                    results = self.search_client.search(
                        search_text=f"{filename_field}:{filename}",
                        top=1,
                        select=select_fields
                    )
                    
                    for result in results:
                        # 컨텐츠가 있는지 확인
                        content = ""
                        for field in content_fields:
                            field_content = result.get(field, "")
                            if field_content and len(field_content) > len(content):
                                content = field_content
                        
                        if content:
                            print(f"✅ 파일 '{filename}' 인덱싱 완료 (대기 시간: {i+1}초)")
                            return True
                    
                    time.sleep(1)  # 1초 대기
                except Exception as e:
                    print(f"⚠️ 인덱싱 대기 중 오류 ({i+1}/{max_wait_time}): {str(e)}")
                    time.sleep(1)
            
            print(f"❌ 파일 '{filename}' 인덱싱 대기 시간 초과 ({max_wait_time}초)")
            return False
            
        except Exception as e:
            print(f"❌ 인덱싱 대기 함수 오류: {str(e)}")
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

    def get_index_schema(self) -> dict:
        """Azure AI Search 인덱스 스키마 조회"""
        try:
            from azure.search.documents.indexes import SearchIndexClient
            
            index_client = SearchIndexClient(
                endpoint=self.search_endpoint,
                credential=self.search_credential
            )
            
            # 현재 인덱스 정보 조회
            index = index_client.get_index(self.index_name)
            
            print(f"📋 인덱스 '{self.index_name}' 스키마:")
            field_names = []
            for field in index.fields:
                print(f"  - {field.name} ({field.type})")
                field_names.append(field.name)
            
            return {
                "status": "success",
                "index_name": self.index_name,
                "fields": field_names
            }
            
        except Exception as e:
            print(f"❌ 인덱스 스키마 조회 오류: {str(e)}")
            return {
                "status": "error",
                "message": f"인덱스 스키마 조회 오류: {str(e)}"
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
            all_files = []  # 모든 파일을 위한 목록 추가
            
            for blob in blob_list:
                file_info = {
                    "name": blob.name,
                    "size": blob.size,
                    "last_modified": blob.last_modified.isoformat() if blob.last_modified else None
                }
                
                # 모든 파일 목록에 추가
                all_files.append(file_info)
                
                if blob.name.startswith("resume_"):
                    resume_files.append({
                        **file_info,
                        "display_name": blob.name.replace("resume_", "")
                    })
                elif blob.name.startswith("job_"):
                    job_files.append({
                        **file_info,
                        "display_name": blob.name.replace("job_", "")
                    })
            
            # 최신 파일 순으로 정렬
            resume_files.sort(key=lambda x: x['last_modified'] or '', reverse=True)
            job_files.sort(key=lambda x: x['last_modified'] or '', reverse=True)
            all_files.sort(key=lambda x: x['last_modified'] or '', reverse=True)
            
            return {
                "status": "success",
                "resume_files": resume_files,
                "job_files": job_files,
                "files": all_files,  # 모든 파일 목록 추가
                "total_files": len(all_files)
            }
            
        except Exception as e:
            print(f"❌ Blob 파일 목록 조회 오류: {str(e)}")
            return {
                "status": "error",
                "message": f"파일 목록 조회 중 오류 발생: {str(e)}"
            }

    def debug_search_index(self) -> dict:
        """Azure AI Search 인덱스의 모든 문서와 스키마 정보를 디버깅용으로 조회"""
        try:
            print(f"🔍 인덱스 '{self.index_name}' 디버깅 시작...")
            
            # 1. 스키마 정보 조회
            schema_info = self.get_index_schema()
            if schema_info["status"] == "error":
                return schema_info
            
            print(f"📋 사용 가능한 필드들: {schema_info['fields']}")
            
            # 2. 모든 문서 조회 (필드 제한 없이)
            try:
                print("📋 모든 문서 조회 중...")
                all_results = self.search_client.search(
                    search_text="*",
                    top=20,  # 최대 20개 문서
                    include_total_count=True
                )
                
                documents = []
                count = 0
                for result in all_results:
                    count += 1
                    doc_info = {}
                    print(f"\n📄 문서 {count}:")
                    
                    # 각 필드의 실제 값 출력
                    for field_name in schema_info['fields']:
                        field_value = result.get(field_name, None)
                        if field_value:
                            if isinstance(field_value, str) and len(field_value) > 100:
                                # 긴 텍스트는 앞부분만 표시
                                display_value = field_value[:100] + "..."
                            else:
                                display_value = field_value
                            print(f"  - {field_name}: {display_value}")
                            doc_info[field_name] = field_value
                    
                    documents.append(doc_info)
                
                print(f"\n✅ 총 {count}개 문서 조회 완료")
                
                return {
                    "status": "success",
                    "schema": schema_info,
                    "documents": documents,
                    "total_count": count
                }
                
            except Exception as e:
                print(f"❌ 문서 조회 오류: {str(e)}")
                return {
                    "status": "error",
                    "message": f"문서 조회 오류: {str(e)}",
                    "schema": schema_info
                }
                
        except Exception as e:
            print(f"❌ 디버깅 함수 오류: {str(e)}")
            return {
                "status": "error",
                "message": f"디버깅 함수 오류: {str(e)}"
            }

    def run_indexer(self) -> dict:
        """Azure AI Search 인덱서를 수동으로 실행하여 Blob Storage의 새 파일들을 인덱싱"""
        try:
            from azure.search.documents.indexes import SearchIndexerClient
            
            indexer_client = SearchIndexerClient(
                endpoint=self.search_endpoint,
                credential=self.search_credential
            )
            
            # 모든 인덱서 목록 조회
            indexers = list(indexer_client.get_indexers())
            print(f"📋 사용 가능한 인덱서들:")
            
            if not indexers:
                return {
                    "status": "error",
                    "message": "사용 가능한 인덱서가 없습니다."
                }
            
            results = []
            for indexer in indexers:
                print(f"  - {indexer.name}")
                
                try:
                    # 인덱서 상태 확인
                    status = indexer_client.get_indexer_status(indexer.name)
                    print(f"    현재 상태: {status.status}")
                    print(f"    마지막 실행: {status.last_result.end_time if status.last_result else 'N/A'}")
                    
                    # 인덱서 실행
                    print(f"🚀 인덱서 '{indexer.name}' 실행 중...")
                    indexer_client.run_indexer(indexer.name)
                    
                    results.append({
                        "indexer_name": indexer.name,
                        "status": "started",
                        "message": f"인덱서 '{indexer.name}' 실행 시작됨"
                    })
                    
                except Exception as e:
                    error_msg = f"인덱서 '{indexer.name}' 실행 오류: {str(e)}"
                    print(f"❌ {error_msg}")
                    results.append({
                        "indexer_name": indexer.name,
                        "status": "error",
                        "message": error_msg
                    })
            
            return {
                "status": "success",
                "message": f"{len(indexers)}개 인덱서 실행 시도 완료",
                "indexers": results
            }
            
        except Exception as e:
            error_msg = f"인덱서 실행 중 오류: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "status": "error", 
                "message": error_msg
            }

    def check_indexer_status(self) -> dict:
        """모든 인덱서의 상태를 확인"""
        try:
            from azure.search.documents.indexes import SearchIndexerClient
            
            indexer_client = SearchIndexerClient(
                endpoint=self.search_endpoint,
                credential=self.search_credential
            )
            
            indexers = list(indexer_client.get_indexers())
            if not indexers:
                return {
                    "status": "error",
                    "message": "사용 가능한 인덱서가 없습니다."
                }
            
            indexer_statuses = []
            for indexer in indexers:
                try:
                    status = indexer_client.get_indexer_status(indexer.name)
                    
                    indexer_info = {
                        "name": indexer.name,
                        "status": status.status.value if status.status else "unknown",
                        "last_execution": status.last_result.end_time.isoformat() if status.last_result and status.last_result.end_time else None,
                        "execution_status": status.last_result.status.value if status.last_result and status.last_result.status else "unknown",
                        "items_processed": status.last_result.item_count if status.last_result else 0,
                        "errors": len(status.last_result.errors) if status.last_result and status.last_result.errors else 0
                    }
                    
                    indexer_statuses.append(indexer_info)
                    
                    print(f"📊 인덱서 '{indexer.name}':")
                    print(f"  - 상태: {indexer_info['status']}")
                    print(f"  - 마지막 실행: {indexer_info['last_execution']}")
                    print(f"  - 처리된 항목: {indexer_info['items_processed']}")
                    print(f"  - 오류 수: {indexer_info['errors']}")
                    
                except Exception as e:
                    print(f"❌ 인덱서 '{indexer.name}' 상태 조회 오류: {str(e)}")
            
            return {
                "status": "success",
                "indexers": indexer_statuses
            }
            
        except Exception as e:
            error_msg = f"인덱서 상태 확인 중 오류: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "status": "error",
                "message": error_msg
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