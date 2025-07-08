import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import MainContent from './components/MainContent';
import ResultSidebar from './components/ResultSidebar';
import { uploadAndTranscribeInterview } from './services/api';

function App() {
  const [jobPostingFile, setJobPostingFile] = useState<File | undefined>();
  const [resumeFile, setResumeFile] = useState<File | undefined>();
  const [interviewFile, setInterviewFile] = useState<File | undefined>();
  const [sttResult, setSttResult] = useState<string>('');
  const [analysisResult, setAnalysisResult] = useState<string>('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  // 문서 분석 결과 상태 추가
  const [documentAnalysisResult, setDocumentAnalysisResult] = useState<string | null>(null);
  const [documentAnalysisError, setDocumentAnalysisError] = useState<string | null>(null);
  
  // 2단계 통합 분석 결과 상태 추가
  const [integratedAnalysisResult, setIntegratedAnalysisResult] = useState<string | null>(null);
  const [integratedAnalysisError, setIntegratedAnalysisError] = useState<string | null>(null);

  // 기존 파일 선택 상태 추가
  const [selectedResumeFile, setSelectedResumeFile] = useState<string | null>(null);
  const [selectedJobFile, setSelectedJobFile] = useState<string | null>(null);

  // 오른쪽 사이드바 상태 추가
  const [isResultSidebarOpen, setIsResultSidebarOpen] = useState(false);

  // 강제 리렌더링을 위한 상태 추가
  const [forceUpdateCounter, setForceUpdateCounter] = useState(0);
  
  // 초기화 신호를 위한 상태 추가
  const [clearSignal, setClearSignal] = useState(0);

  const handleJobPostingUpload = (file: File) => {
    setJobPostingFile(file);
    // 새 파일 업로드 시 기존 파일 선택 해제
    setSelectedJobFile(null);
  };

  const handleResumeUpload = (file: File) => {
    setResumeFile(file);
    // 새 파일 업로드 시 기존 파일 선택 해제
    setSelectedResumeFile(null);
  };

  const handleInterviewUpload = async (file: File) => {
    setInterviewFile(file);
    
    // 면접 녹음 파일 업로드 시 자동으로 STT 처리
    try {
      console.log('🎤 면접 녹음 파일 업로드 + STT 시작:', file.name);
      setSttResult(''); // 기존 STT 결과 초기화
      
      const result = await uploadAndTranscribeInterview(file);
      
      if (result.status === 'success' && result.transcription) {
        console.log('✅ STT 완료:', result.transcription.substring(0, 100) + '...');
        setSttResult(result.transcription);
      } else {
        console.error('❌ STT 실패:', result.message);
        // STT 실패해도 파일은 유지하되, 사용자에게 알림
        alert(`STT 처리 실패: ${result.message}\n\n파일은 업로드되었지만 음성-텍스트 변환에 실패했습니다.`);
      }
    } catch (error) {
      console.error('❌ STT 처리 중 오류:', error);
      alert(`STT 처리 중 오류가 발생했습니다: ${error}\n\n파일은 업로드되었지만 음성-텍스트 변환에 실패했습니다.`);
    }
  };

  const handleRemoveJobPosting = () => {
    setJobPostingFile(undefined);
    setSelectedJobFile(null);
  };

  const handleRemoveResume = () => {
    setResumeFile(undefined);
    setSelectedResumeFile(null);
  };

  const handleRemoveInterview = () => {
    setInterviewFile(undefined);
  };

  // 전체 초기화 함수 (Sidebar에서 호출)
  const handleResetAll = () => {
    // 파일들 초기화
    setJobPostingFile(undefined);
    setResumeFile(undefined);
    setInterviewFile(undefined);
    setSelectedResumeFile(null);
    setSelectedJobFile(null);
    
    // 분석 결과 초기화
    setDocumentAnalysisResult(null);
    setDocumentAnalysisError(null);
    setIntegratedAnalysisResult(null);
    setIntegratedAnalysisError(null);
    setSttResult('');
    setAnalysisResult('');
    
    // 로컬 상태 초기화 신호 발송
    setClearSignal(prev => prev + 1);
    
    console.log('🔄 App - 전체 초기화 완료');
  };

  // 기존 파일 선택 핸들러 추가
  const handleSelectedResumeChange = (filename: string | null) => {
    setSelectedResumeFile(filename);
    // 기존 파일 선택 시 업로드된 파일 해제
    if (filename) {
      setResumeFile(undefined);
    }
  };

  const handleSelectedJobChange = (filename: string | null) => {
    setSelectedJobFile(filename);
    // 기존 파일 선택 시 업로드된 파일 해제
    if (filename) {
      setJobPostingFile(undefined);
    }
  };

  const handleSidebarToggle = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  // 오른쪽 사이드바 토글
  const handleResultSidebarToggle = () => {
    setIsResultSidebarOpen(!isResultSidebarOpen);
  };

  // 문서 분석 결과 업데이트 함수
  const handleDocumentAnalysisUpdate = (result: string | null, error: string | null) => {
    setDocumentAnalysisResult(result);
    setDocumentAnalysisError(error);
  };

  // 통합 분석 결과 업데이트 함수
  const handleIntegratedAnalysisUpdate = (result: string | null, error: string | null) => {
    setIntegratedAnalysisResult(result);
    setIntegratedAnalysisError(error);
  };

  // 분석 결과 저장 핸들러
  const handleSaveResult = (data: any) => {
    console.log('분석 결과 저장됨:', data);
    // 필요하다면 추가 처리 로직
  };

  // 저장된 결과 불러오기 핸들러
  const handleLoadResult = (result: any) => {
    console.log('💾 저장된 결과 불러오기:', result);
    console.log('📊 데이터 구조:', JSON.stringify(result, null, 2));
    
    // 결과 데이터를 현재 상태에 적용
    if (result.results) {
      console.log('📄 분석 결과 복원 중...');
      
      if (result.results.document_analysis && result.results.document_analysis.trim()) {
        console.log('✅ 문서 분석 결과 복원:', result.results.document_analysis.substring(0, 100) + '...');
        console.log('🔧 setDocumentAnalysisResult 호출 직전');
        
        // 강제로 상태 업데이트 (React 18 배칭 문제 해결)
        setTimeout(() => {
          setDocumentAnalysisResult(result.results.document_analysis);
          setDocumentAnalysisError(null);
          console.log('🔧 setDocumentAnalysisResult 호출 완료 (setTimeout)');
          
          // 강제 리렌더링 트리거
          setForceUpdateCounter(prev => prev + 1);
          console.log('🔄 강제 리렌더링 트리거');
        }, 0);
        
      } else {
        console.log('⚠️ 문서 분석 결과가 비어있음');
      }
      
      if (result.results.interview_stt && result.results.interview_stt.trim()) {
        console.log('✅ STT 결과 복원:', result.results.interview_stt.substring(0, 50) + '...');
        setSttResult(result.results.interview_stt);
      } else {
        console.log('⚠️ STT 결과가 비어있음');
      }
      
      if (result.results.integrated_analysis && result.results.integrated_analysis.trim()) {
        console.log('✅ 통합 분석 결과 복원:', result.results.integrated_analysis.substring(0, 100) + '...');
        setTimeout(() => {
          setIntegratedAnalysisResult(result.results.integrated_analysis);
          setIntegratedAnalysisError(null);
          console.log('🔧 setIntegratedAnalysisResult 호출 완료 (setTimeout)');
          
          // 강제 리렌더링 트리거
          setForceUpdateCounter(prev => prev + 1);
          console.log('🔄 강제 리렌더링 트리거 (통합분석)');
        }, 0);
      } else {
        console.log('⚠️ 통합 분석 결과가 비어있음');
      }
    } else {
      console.log('❌ results 필드가 없습니다:', Object.keys(result));
    }
    
    // 파일 정보도 업데이트 (파일명에서 prefix 제거)
    if (result.metadata) {
      console.log('📁 파일 정보 복원 중...');
      
      if (result.metadata.resume_file) {
        // "resume_" prefix 제거
        const cleanResumeFile = result.metadata.resume_file.replace('resume_', '');
        console.log('✅ 이력서 파일 정보 복원:', result.metadata.resume_file, '→', cleanResumeFile);
        setSelectedResumeFile(result.metadata.resume_file); // 전체 파일명 사용
        setResumeFile(undefined);
      }
      
      if (result.metadata.job_file) {
        // "job_" prefix 제거
        const cleanJobFile = result.metadata.job_file.replace('job_', '');
        console.log('✅ 채용공고 파일 정보 복원:', result.metadata.job_file, '→', cleanJobFile);
        setSelectedJobFile(result.metadata.job_file); // 전체 파일명 사용
        setJobPostingFile(undefined);
      }
    } else {
      console.log('❌ metadata 필드가 없습니다:', Object.keys(result));
    }
    
    // 사이드바 닫기 (선택사항)
    setIsResultSidebarOpen(false);
    
    // 현재 상태 확인
    console.log('🔍 복원 후 상태 확인:');
    console.log('  - documentAnalysisResult:', result.results?.document_analysis ? '✅ 있음' : '❌ 없음');
    console.log('  - selectedResumeFile:', result.metadata?.resume_file || '❌ 없음');
    console.log('  - selectedJobFile:', result.metadata?.job_file || '❌ 없음');
    
    console.log('🎉 결과 복원 완료!');
    

  };

  // 현재 결과 정보 준비
  const currentResults = {
    documentAnalysis: documentAnalysisResult || undefined,
    integratedAnalysis: integratedAnalysisResult || undefined,
    sttResult: sttResult || undefined,
    resumeFile: resumeFile?.name || selectedResumeFile || undefined,
    jobFile: jobPostingFile?.name || selectedJobFile || undefined
  };

  const handleStartAnalysis = () => {
    setIsAnalyzing(true);
    setSttResult('');
    setAnalysisResult('');
    
    // Simulate STT processing
    setTimeout(() => {
      setSttResult(`면접관: 안녕하세요. 자기소개를 부탁드립니다.

면접자: 안녕하세요. 저는 컴퓨터공학과를 졸업하고 웹 개발 분야에서 2년간 경험을 쌓은 김지훈입니다. 대학 시절 팀 프로젝트를 통해 협업의 중요성을 배웠고, 이전 회사에서는 프론트엔드 개발자로 일하며 사용자 경험 개선에 많은 관심을 가지게 되었습니다. 특히 React와 TypeScript를 활용한 개발에 능숙하며, 항상 새로운 기술을 학습하고 적용하는 것을 즐깁니다.

면접관: 팀 프로젝트에서 어려웠던 점은 무엇인가요?

면접자: 팀 프로젝트에서 가장 어려웠던 점은 팀원들 간의 의견 차이를 조율하는 것이었습니다. 각자 다른 개발 스타일과 우선순위를 가지고 있어서 초기에는 갈등이 있었습니다. 하지만 정기적인 회의를 통해 서로의 의견을 충분히 듣고, 프로젝트 목표에 맞는 최적의 방안을 함께 찾아나가는 과정을 통해 해결할 수 있었습니다. 이 경험을 통해 소통의 중요성을 깨달았습니다.`);
    }, 2000);
    
    // Simulate analysis processing
    setTimeout(() => {
      setAnalysisResult(`**면접 분석 결과 요약**

**1. 전체적인 인상**
- 면접자는 차분하고 논리적인 답변을 제시했습니다
- 질문에 대한 이해도가 높고 구체적인 경험을 바탕으로 답변했습니다
- 자신감 있는 태도로 면접에 임했습니다

**2. 기술 역량**
- React, TypeScript 등 최신 웹 기술에 대한 경험 보유
- 실무 경험 2년으로 기본기가 탄탄함
- 새로운 기술 학습에 대한 적극적인 자세

**3. 소프트 스킬**
- 팀워크: 협업 경험이 풍부하고 갈등 해결 능력 보유
- 소통 능력: 명확하고 구조적인 답변 제시
- 학습 의욕: 지속적인 성장 의지 표현

**4. 채용 적합성**
- KT DS의 기술 스택과 잘 맞음
- 협업 문화에 잘 적응할 것으로 예상
- 성장 가능성이 높음

**종합 평가: A- (85점)**
기술 역량과 인성 모두 우수하며, KT DS 신입사원으로 적합한 후보자입니다.

**면접 추천 질문**
1. 최근 관심있게 공부하고 있는 기술이 있나요?
2. 어려운 기술적 문제를 해결했던 경험이 있다면 공유해주세요.
3. KT DS에서 어떤 기여를 하고 싶으신가요?`);
      setIsAnalyzing(false);
    }, 4000);
  };

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar
        jobPostingFile={jobPostingFile}
        resumeFile={resumeFile}
        interviewFile={interviewFile}
        onJobPostingUpload={handleJobPostingUpload}
        onResumeUpload={handleResumeUpload}
        onInterviewUpload={handleInterviewUpload}
        onRemoveJobPosting={handleRemoveJobPosting}
        onRemoveResume={handleRemoveResume}
        onRemoveInterview={handleRemoveInterview}
        onStartAnalysis={handleStartAnalysis}
        isAnalyzing={isAnalyzing}
        isOpen={isSidebarOpen}
        onToggle={handleSidebarToggle}
        onDocumentAnalysisUpdate={handleDocumentAnalysisUpdate}
        selectedResumeFile={selectedResumeFile}
        selectedJobFile={selectedJobFile}
        onSelectedResumeChange={handleSelectedResumeChange}
        onSelectedJobChange={handleSelectedJobChange}
        onIntegratedAnalysisUpdate={handleIntegratedAnalysisUpdate}
        sttResult={sttResult}
        documentAnalysisResult={documentAnalysisResult}
        onResetAll={handleResetAll}
      />
      <MainContent
        jobPostingFile={jobPostingFile}
        resumeFile={resumeFile}
        interviewFile={interviewFile}
        sttResult={sttResult}
        analysisResult={analysisResult}
        isAnalyzing={isAnalyzing}
        documentAnalysisResult={documentAnalysisResult}
        documentAnalysisError={documentAnalysisError}
        selectedResumeFile={selectedResumeFile}
        selectedJobFile={selectedJobFile}
        integratedAnalysisResult={integratedAnalysisResult}
        integratedAnalysisError={integratedAnalysisError}
        forceUpdateCounter={forceUpdateCounter}
        clearSignal={clearSignal}
      />
      <ResultSidebar
        isOpen={isResultSidebarOpen}
        onToggle={handleResultSidebarToggle}
        onSaveResult={handleSaveResult}
        onLoadResult={handleLoadResult}
        currentResults={currentResults}
      />
    </div>
  );
}

export default App;