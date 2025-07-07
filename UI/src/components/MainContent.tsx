import React, { useState } from 'react';
import { FileText, MessageSquare, Send, User, Mic, CheckCircle } from 'lucide-react';

interface MainContentProps {
  jobPostingFile?: File;
  resumeFile?: File;
  interviewFile?: File;
  sttResult: string;
  analysisResult: string;
  isAnalyzing: boolean;
}

const MainContent: React.FC<MainContentProps> = ({
  jobPostingFile,
  resumeFile,
  interviewFile,
  sttResult,
  analysisResult,
  isAnalyzing
}) => {
  const [prompt, setPrompt] = useState('');
  const [chatMessages, setChatMessages] = useState<Array<{role: 'user' | 'assistant', content: string}>>([]);
  const [isQuerying, setIsQuerying] = useState(false);

  const handleSubmitPrompt = async () => {
    if (!prompt.trim()) return;
    
    setIsQuerying(true);
    const userMessage = { role: 'user' as const, content: prompt };
    setChatMessages(prev => [...prev, userMessage]);
    
    // Simulate API call
    setTimeout(() => {
      const assistantMessage = {
        role: 'assistant' as const,
        content: `**면접자의 대인관계 역량 분석 결과:**

**1. 의사소통 능력**
- 면접자는 질문에 대해 명확하고 구체적으로 답변했습니다
- 전문 용어를 적절히 사용하면서도 이해하기 쉽게 설명했습니다
- 상대방의 질문 의도를 정확히 파악하고 답변했습니다

**2. 협업 및 팀워크**
- 이전 프로젝트에서의 팀 협업 경험을 구체적으로 제시했습니다
- 갈등 상황에서의 해결 방법을 논리적으로 설명했습니다
- 타인의 의견을 존중하고 수용하는 자세를 보였습니다

**3. 리더십 잠재력**
- 주도적으로 문제를 해결하려는 의지를 보였습니다
- 책임감 있는 태도로 업무에 임하는 모습을 확인했습니다

**종합 평가: B+ (80점)**
대인관계 역량이 우수하며, KT DS의 협업 문화에 잘 적응할 것으로 예상됩니다.`
      };
      setChatMessages(prev => [...prev, assistantMessage]);
      setIsQuerying(false);
    }, 2000);
    
    setPrompt('');
  };

  return (
    <div className="flex-1 p-8 bg-gray-50 overflow-y-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">
          KT DS 신입사원 면접 분석 및 평가 보조 Agent
        </h1>
        <p className="text-gray-600">
          AI 기반 면접 분석을 통해 객관적이고 체계적인 평가를 제공합니다
        </p>
      </div>

      {/* Uploaded Files Status */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">업로드된 파일</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center space-x-3 p-4 bg-gray-50 rounded-lg">
            <FileText className="w-6 h-6 text-blue-600" />
            <div>
              <p className="text-sm font-medium text-gray-700">채용공고</p>
              <p className="text-xs text-gray-500">
                {jobPostingFile ? (
                  <span className="flex items-center space-x-1">
                    <CheckCircle className="w-3 h-3 text-green-600" />
                    <span>{jobPostingFile.name}</span>
                  </span>
                ) : (
                  '업로드 필요'
                )}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3 p-4 bg-gray-50 rounded-lg">
            <User className="w-6 h-6 text-green-600" />
            <div>
              <p className="text-sm font-medium text-gray-700">이력서</p>
              <p className="text-xs text-gray-500">
                {resumeFile ? (
                  <span className="flex items-center space-x-1">
                    <CheckCircle className="w-3 h-3 text-green-600" />
                    <span>{resumeFile.name}</span>
                  </span>
                ) : (
                  '업로드 필요'
                )}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3 p-4 bg-gray-50 rounded-lg">
            <Mic className="w-6 h-6 text-purple-600" />
            <div>
              <p className="text-sm font-medium text-gray-700">면접 녹음</p>
              <p className="text-xs text-gray-500">
                {interviewFile ? (
                  <span className="flex items-center space-x-1">
                    <CheckCircle className="w-3 h-3 text-green-600" />
                    <span>{interviewFile.name}</span>
                  </span>
                ) : (
                  '업로드 필요'
                )}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* STT Result */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">면접 STT 결과</h2>
        <div className="bg-gray-50 rounded-lg p-4 max-h-40 overflow-y-auto">
          {sttResult ? (
            <p className="text-sm text-gray-700 leading-relaxed">{sttResult}</p>
          ) : (
            <p className="text-sm text-gray-500 italic">
              {isAnalyzing ? '음성을 텍스트로 변환 중...' : '면접 녹음 파일을 업로드하고 분석을 시작하세요'}
            </p>
          )}
        </div>
      </div>

      {/* Analysis Result */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">분석 결과 요약</h2>
        <div className="bg-gray-50 rounded-lg p-4 max-h-60 overflow-y-auto">
          {analysisResult ? (
            <div className="prose prose-sm max-w-none">
              <pre className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap font-sans">
                {analysisResult}
              </pre>
            </div>
          ) : (
            <p className="text-sm text-gray-500 italic">
              {isAnalyzing ? 'AI가 면접 내용을 분석하고 있습니다...' : '파일을 업로드하고 분석을 시작하면 결과가 여기에 표시됩니다'}
            </p>
          )}
        </div>
      </div>

      {/* Prompt Input */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">추가 질문</h2>
        <div className="space-y-4">
          <div className="flex space-x-3">
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="면접자의 대인관계 역량에 대해 분석해줘"
              className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
              rows={3}
            />
            <button
              onClick={handleSubmitPrompt}
              disabled={!prompt.trim() || isQuerying}
              className={`px-4 py-2 rounded-lg font-medium transition-all self-start
                ${prompt.trim() && !isQuerying
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                }`}
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
          
          {/* Chat Messages */}
          {chatMessages.length > 0 && (
            <div className="space-y-4 max-h-80 overflow-y-auto">
              {chatMessages.map((message, index) => (
                <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-3xl p-3 rounded-lg ${
                    message.role === 'user' 
                      ? 'bg-blue-100 text-blue-800' 
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {message.role === 'assistant' ? (
                      <div className="prose prose-sm max-w-none">
                        <pre className="whitespace-pre-wrap font-sans text-sm">{message.content}</pre>
                      </div>
                    ) : (
                      <p className="text-sm">{message.content}</p>
                    )}
                  </div>
                </div>
              ))}
              {isQuerying && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 p-3 rounded-lg">
                    <p className="text-sm text-gray-600">분석 중...</p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MainContent;