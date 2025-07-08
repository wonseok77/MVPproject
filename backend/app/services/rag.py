from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY", "")
embeddings = AzureOpenAIEmbeddings(model=os.getenv("AZURE_OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002"))

llm = AzureChatOpenAI(
    model=os.getenv("AZURE_OPENAI_MODEL_1", "gpt-4"),
    temperature=0,
    api_version="2025-01-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
    azure_deployment=os.getenv("AZURE_OPENAI_MODEL_1", "gpt-4"),
)

from langchain_community.retrievers import AzureAISearchRetriever

retriever = AzureAISearchRetriever(
        service_name=os.getenv("AZURE_AI_SEARCH_SERVICE_NAME", ""),
        top_k=5,
        index_name=os.getenv("AZURE_AI_SEARCH_INDEX_NAME", ""), # ai search 서비스에서 사용할 인덱스 이름
        content_key="chunk", # 검색된 결과에서 문서의 page_content로 사용할 키, 주의) 인덱스에서 검색대상될 필드 명이 아니다.
        api_key=os.getenv("AZURE_AI_SEARCH_API_KEY", "") # Azure Search Service 의 key
    )


from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import AzureChatOpenAI

prompt = ChatPromptTemplate.from_template(
    """당신은 면접관을 위한 지원자 평가 및 분석 전문가입니다.
    면접관이 지원자를 효과적으로 평가할 수 있도록 도움을 제공합니다.
    
    Context: {context}

    Question: {question}"""
    )

llm2 = AzureChatOpenAI(
    model=os.getenv("AZURE_OPENAI_MODEL_1", "gpt-4o"),
    temperature=0,
    api_version="2024-11-20",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
    azure_deployment=os.getenv("AZURE_OPENAI_MODEL_1", "gpt-4o"),
)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm2
    | StrOutputParser()
)

# 함수로 만들어서 다른 곳에서 사용 가능하게 하기
def analyze_candidate_profile(question: str) -> str:
    """
    면접관을 위한 지원자 프로필 분석 함수
    
    Args:
        question: 면접관의 질문 (예: "이 지원자의 기술 스택이 백엔드 개발자 포지션에 적합한가?")
        
    Returns:
        str: AI 분석 결과
    """
    try:
        answer = chain.invoke(question)
        return answer
    except Exception as e:
        return f"분석 중 오류가 발생했습니다: {str(e)}"

def analyze_candidate_match(resume_text: str, job_posting_text: str) -> dict:
    """
    지원자-채용공고 매칭 분석 (메인 함수)
    
    Args:
        resume_text: 지원자 이력서 내용
        job_posting_text: 채용공고 내용
        
    Returns:
        dict: 분석 결과 + 추천 질문
    """
    analysis_question = f"""
    다음 지원자와 채용공고를 분석해서 깔끔하게 요약해주세요:
    
    [채용공고]
    {job_posting_text}
    
    [지원자 이력서]
    {resume_text}
    
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
    
    result = analyze_candidate_profile(analysis_question)
    return {
        "analysis": result,
        "status": "success"
    }

def ask_specific_question(question: str, resume_text: str = "", job_posting_text: str = "") -> dict:
    """
    특정 질문에 대한 답변 (자유 질의응답)
    """
    context = ""
    if resume_text:
        context += f"\n[이력서 참고]\n{resume_text}"
    if job_posting_text:
        context += f"\n[채용공고 참고]\n{job_posting_text}"
    
    full_question = f"{question}{context}"
    result = analyze_candidate_profile(full_question)
    
    return {
        "type": "specific_question",
        "question": question,
        "answer": result
    }

# 기존 테스트 코드는 주석 처리
# chain.invoke("roundrobin team이란? 예시코드")
