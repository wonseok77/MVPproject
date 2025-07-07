"""
임시 JSON 파일 저장소 서비스 (ChromaDB 대신)
"""
import logging
import uuid
from typing import Dict, Any, List
import json
import os
from ..config import settings

logger = logging.getLogger(__name__)

class TempStoreService:
    """임시 파일 저장소 서비스 클래스"""
    
    def __init__(self):
        """임시 저장소 초기화"""
        try:
            # 저장소 디렉토리 생성
            self.storage_dir = settings.chroma_persist_dir
            os.makedirs(self.storage_dir, exist_ok=True)
            
            # 저장소 파일 경로
            self.storage_file = os.path.join(self.storage_dir, "interview_analysis.json")
            
            # 메모리 저장소 초기화
            self.storage = self._load_storage()
            
            logger.info("임시 저장소 초기화 완료")
            
        except Exception as e:
            logger.error(f"저장소 초기화 중 오류 발생: {str(e)}")
            raise Exception(f"저장소 초기화 실패: {str(e)}")
    
    def _load_storage(self) -> Dict[str, Any]:
        """저장소 파일 로드"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.warning(f"저장소 로드 실패, 빈 저장소 생성: {str(e)}")
            return {}
    
    def _save_storage(self):
        """저장소 파일 저장"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.storage, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"저장소 저장 실패: {str(e)}")
            raise Exception(f"저장소 저장 실패: {str(e)}")
    
    def save_analysis_result(
        self,
        candidate_name: str,
        position: str,
        summary: str,
        strengths: str,
        weaknesses: str
    ) -> str:
        """
        분석 결과를 저장소에 저장합니다.
        
        Args:
            candidate_name: 지원자 이름
            position: 지원 직무
            summary: 평가 요약
            strengths: 강점
            weaknesses: 약점
            
        Returns:
            str: 생성된 UUID
        """
        try:
            # UUID 생성
            document_id = str(uuid.uuid4())
            
            # 데이터 구성
            data = {
                "id": document_id,
                "candidate_name": candidate_name,
                "position": position,
                "summary": summary,
                "strengths": strengths,
                "weaknesses": weaknesses,
                "document_type": "interview_analysis"
            }
            
            # 저장소에 추가
            self.storage[document_id] = data
            
            # 파일에 저장
            self._save_storage()
            
            logger.info(f"분석 결과 저장 완료: {document_id}")
            return document_id
            
        except Exception as e:
            logger.error(f"분석 결과 저장 중 오류 발생: {str(e)}")
            raise Exception(f"분석 결과 저장 실패: {str(e)}")
    
    def get_analysis_result(self, document_id: str) -> Dict[str, Any]:
        """
        저장된 분석 결과를 조회합니다.
        
        Args:
            document_id: 문서 ID
            
        Returns:
            Dict: 분석 결과
        """
        try:
            if document_id not in self.storage:
                raise Exception(f"문서를 찾을 수 없습니다: {document_id}")
            
            return self.storage[document_id]
            
        except Exception as e:
            logger.error(f"분석 결과 조회 중 오류 발생: {str(e)}")
            raise Exception(f"분석 결과 조회 실패: {str(e)}")
    
    def search_analyses(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        분석 결과를 검색합니다.
        
        Args:
            query: 검색 쿼리
            limit: 결과 제한 수
            
        Returns:
            list: 검색 결과
        """
        try:
            # 간단한 텍스트 검색 (대소문자 구분 안함)
            results = []
            query_lower = query.lower()
            
            for doc_id, data in self.storage.items():
                # 검색 대상 텍스트 구성
                search_text = f"{data.get('candidate_name', '')} {data.get('position', '')} {data.get('summary', '')} {data.get('strengths', '')} {data.get('weaknesses', '')}".lower()
                
                if query_lower in search_text:
                    result = data.copy()
                    result["similarity_score"] = 1.0  # 임시로 1.0 설정
                    results.append(result)
                    
                    if len(results) >= limit:
                        break
            
            return results
            
        except Exception as e:
            logger.error(f"분석 결과 검색 중 오류 발생: {str(e)}")
            raise Exception(f"분석 결과 검색 실패: {str(e)}")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """컬렉션 통계 정보를 반환합니다."""
        try:
            count = len(self.storage)
            return {
                "collection_name": "interview_analysis",
                "document_count": count,
                "persist_directory": self.storage_dir,
                "storage_type": "JSON 파일"
            }
        except Exception as e:
            logger.error(f"컬렉션 통계 조회 중 오류 발생: {str(e)}")
            return {"error": str(e)}

# 서비스 인스턴스 생성
chroma_store_service = TempStoreService() 