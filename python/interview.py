import streamlit as st
from typing import Optional
import os

st.set_page_config(page_title="KT DS 신입사원 면접 분석 및 평가 보조 Agent", layout="wide")

# ---- 사이드바 ----
st.sidebar.header("파일 업로드")
job_file = st.sidebar.file_uploader("채용공고 업로드 (PDF, DOC, DOCX)", type=["pdf", "doc", "docx"], key="job")
resume_file = st.sidebar.file_uploader("이력서 업로드 (PDF, DOC, DOCX)", type=["pdf", "doc", "docx"], key="resume")
interview_audio = st.sidebar.file_uploader("면접 녹음 파일 업로드 (MP3, WAV)", type=["mp3", "wav"], key="audio")

analyze_btn = st.sidebar.button("전송 및 분석 시작")

# ---- 본문 ----
st.title("KT DS 신입사원 면접 분석 및 평가 보조 Agent")

# 업로드된 파일명 표시
def get_filename(file) -> Optional[str]:
    if file is not None:
        return file.name
    return None

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"**채용공고 파일:** {get_filename(job_file) or '-'}")
with col2:
    st.markdown(f"**이력서 파일:** {get_filename(resume_file) or '-'}")

st.markdown("---")

# 면접 STT 결과 표시 영역
st.subheader("면접 STT 결과")
stt_result = st.empty()

# 분석 결과 요약 영역
st.subheader("분석 결과 요약")
result_summary = st.empty()

# 프롬프트 입력창
st.markdown("---")
st.markdown("#### 추가 분석 요청")
def_prompt = "면접자의 대인관계 역량에 대해 분석해줘"
prompt = st.text_area("프롬프트 입력", value=def_prompt, height=80)

if st.button("GPT-4로 분석 요청"):
    # 실제 GPT-4 API 연동 필요 (예시)
    gpt_response = f"[GPT-4 응답 예시] '{prompt}'에 대한 분석 결과입니다. (실제 API 연동 필요)"
    st.markdown(f"**GPT-4 응답:**\n\n{gpt_response}")

# 파일 MIME 타입 판별 및 텍스트 변환 함수 구조 (구현 예시)
def extract_text_from_file(uploaded_file) -> str:
    """
    업로드된 파일의 MIME 타입을 판별하고, pdf/doc/docx는 텍스트로 변환하여 반환.
    (구현 필요: pdfplumber, python-docx 등 활용)
    """
    if uploaded_file is None:
        return ""
    # TODO: MIME 타입 판별 및 텍스트 추출 구현
    return f"[텍스트 변환 예시] {uploaded_file.name}"

# 분석 버튼 동작 예시
def analyze():
    job_text = extract_text_from_file(job_file)
    resume_text = extract_text_from_file(resume_file)
    stt_text = "[STT 변환 예시] 면접 녹음 파일에서 추출된 텍스트"
    stt_result.markdown(stt_text)
    # OpenAI 등 분석 결과 예시
    summary = "[분석 요약 예시] 이력서와 면접 내용을 기반으로 한 평가 결과입니다. (실제 분석 로직 필요)"
    result_summary.markdown(summary)

if analyze_btn:
    analyze()

