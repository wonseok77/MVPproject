"""
Azure OpenAI API 서비스
"""
import logging
from openai import AzureOpenAI
from ..config import settings
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AzureOpenAIService:
    """Azure OpenAI API 서비스 클래스"""
    
    def __init__(self):
        """Azure OpenAI 클라이언트 초기화"""
        self.client = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint
        )
    
    def analyze_interview(
        self, 
        candidate_name: str,
        position: str,
        resume_text: str,
        job_posting_text: str,
        interview_text: str
    ) -> Dict[str, str]:
        """
        면접 분석을 수행하고 결과를 반환합니다.
        
        Args:
            candidate_name: 지원자 이름
            position: 지원 직무
            resume_text: 이력서 텍스트
            job_posting_text: 채용공고 텍스트
            interview_text: 면접 내용 텍스트
            
        Returns:
            Dict containing summary, strengths, weaknesses
        """
        try:
            # 면접 분석 프롬프트 구성
            prompt = self._create_analysis_prompt(
                candidate_name, position, resume_text, job_posting_text, interview_text
            )
            
            # Azure OpenAI API 호출
            response = self.client.chat.completions.create(
                model=settings.azure_openai_deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 KT DS의 전문 면접관입니다. 면접자의 답변을 종합적으로 분석하고 평가해주세요."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            # 응답 파싱
            content = response.choices[0].message.content
            if content is None:
                raise Exception("OpenAI 응답이 비어있습니다.")
            return self._parse_response(content)
            
        except Exception as e:
            logger.error(f"면접 분석 중 오류 발생: {str(e)}")
            raise Exception(f"면접 분석 실패: {str(e)}")
    
    def _create_analysis_prompt(
        self,
        candidate_name: str,
        position: str,
        resume_text: str,
        job_posting_text: str,
        interview_text: str
    ) -> str:
        """면접 분석 프롬프트 생성"""
        return f"""
다음 정보를 바탕으로 면접자를 종합적으로 분석하고 평가해주세요:

**지원자 정보:**
- 이름: {candidate_name}
- 지원 직무: {position}

**이력서 내용:**
{resume_text}

**채용공고 내용:**
{job_posting_text}

**면접 내용:**
{interview_text}

**분석 요청:**
위 정보를 바탕으로 다음 형식으로 분석 결과를 제공해주세요:

평가 요약:
[지원자의 전체적인 면접 성과와 직무 적합성에 대한 종합적인 평가를 3-4문장으로 작성]

강점:
[지원자의 주요 강점들을 구체적으로 나열하고 설명]

약점:
[지원자의 개선이 필요한 부분들을 구체적으로 나열하고 개선 방안 제시]

**주의사항:**
- 객관적이고 공정한 평가를 해주세요
- 구체적인 예시와 근거를 제시해주세요
- 건설적인 피드백을 포함해주세요
- 반드시 "평가 요약:", "강점:", "약점:" 형식을 지켜주세요
"""

    def _parse_response(self, content: str) -> Dict[str, str]:
        """GPT 응답을 파싱하여 구조화된 데이터로 변환"""
        try:
            result = {
                "summary": "",
                "strengths": "",
                "weaknesses": ""
            }
            
            lines = content.strip().split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                
                if line.startswith('평가 요약:'):
                    current_section = 'summary'
                    # 콜론 뒤의 내용이 있다면 추가
                    after_colon = line.split(':', 1)[1].strip()
                    if after_colon:
                        result[current_section] = after_colon
                elif line.startswith('강점:'):
                    current_section = 'strengths'
                    after_colon = line.split(':', 1)[1].strip()
                    if after_colon:
                        result[current_section] = after_colon
                elif line.startswith('약점:'):
                    current_section = 'weaknesses'
                    after_colon = line.split(':', 1)[1].strip()
                    if after_colon:
                        result[current_section] = after_colon
                elif current_section and line:
                    # 현재 섹션에 내용 추가
                    if result[current_section]:
                        result[current_section] += f"\n{line}"
                    else:
                        result[current_section] = line
            
            # 빈 섹션이 있으면 기본값 설정
            if not result["summary"]:
                result["summary"] = "분석 결과를 파싱하는 중 오류가 발생했습니다."
            if not result["strengths"]:
                result["strengths"] = "강점 분석 결과를 파싱하는 중 오류가 발생했습니다."
            if not result["weaknesses"]:
                result["weaknesses"] = "약점 분석 결과를 파싱하는 중 오류가 발생했습니다."
                
            return result
            
        except Exception as e:
            logger.error(f"응답 파싱 중 오류 발생: {str(e)}")
            return {
                "summary": "분석 결과를 파싱하는 중 오류가 발생했습니다.",
                "strengths": f"응답 파싱 실패: {str(e)}",
                "weaknesses": f"응답 파싱 실패: {str(e)}"
            }

# 서비스 인스턴스 생성
azure_openai_service = AzureOpenAIService() 