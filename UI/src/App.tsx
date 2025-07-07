import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import MainContent from './components/MainContent';

function App() {
  const [jobPostingFile, setJobPostingFile] = useState<File | undefined>();
  const [resumeFile, setResumeFile] = useState<File | undefined>();
  const [interviewFile, setInterviewFile] = useState<File | undefined>();
  const [sttResult, setSttResult] = useState<string>('');
  const [analysisResult, setAnalysisResult] = useState<string>('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const handleJobPostingUpload = (file: File) => {
    setJobPostingFile(file);
  };

  const handleResumeUpload = (file: File) => {
    setResumeFile(file);
  };

  const handleInterviewUpload = (file: File) => {
    setInterviewFile(file);
  };

  const handleRemoveJobPosting = () => {
    setJobPostingFile(undefined);
  };

  const handleRemoveResume = () => {
    setResumeFile(undefined);
  };

  const handleRemoveInterview = () => {
    setInterviewFile(undefined);
  };

  const handleSidebarToggle = () => {
    setIsSidebarOpen(!isSidebarOpen);
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
      />
      <MainContent
        jobPostingFile={jobPostingFile}
        resumeFile={resumeFile}
        interviewFile={interviewFile}
        sttResult={sttResult}
        analysisResult={analysisResult}
        isAnalyzing={isAnalyzing}
      />
    </div>
  );
}

export default App;