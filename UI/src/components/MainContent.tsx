import React, { useState, useEffect } from 'react';
import { FileText, MessageSquare, Send, User, Mic, CheckCircle, BarChart3 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface MainContentProps {
  jobPostingFile?: File;
  resumeFile?: File;
  interviewFile?: File;
  sttResult: string;
  analysisResult: string;
  isAnalyzing: boolean;
  documentAnalysisResult: string | null;
  documentAnalysisError: string | null;
  selectedResumeFile: string | null;
  selectedJobFile: string | null;
  integratedAnalysisResult: string | null;
  integratedAnalysisError: string | null;
  forceUpdateCounter: number;
  clearSignal: number; // 초기화 신호
}

const MainContent: React.FC<MainContentProps> = ({
  jobPostingFile,
  resumeFile,
  interviewFile,
  sttResult,
  analysisResult,
  isAnalyzing,
  documentAnalysisResult,
  documentAnalysisError,
  selectedResumeFile,
  selectedJobFile,
  integratedAnalysisResult,
  integratedAnalysisError,
  forceUpdateCounter,
  clearSignal
}) => {
  const [prompt, setPrompt] = useState('');
  const [chatMessages, setChatMessages] = useState<Array<{role: 'user' | 'assistant', content: string}>>([]);
  const [isQuerying, setIsQuerying] = useState(false);
  
  // 로컬 상태로 데이터 관리 (강제로!)
  const [localDocumentResult, setLocalDocumentResult] = useState<string | null>(null);
  const [localIntegratedResult, setLocalIntegratedResult] = useState<string | null>(null);

  // Props 변경 감지를 위한 useEffect
  useEffect(() => {
    console.log('🔍 MainContent - documentAnalysisResult 변경 감지:', documentAnalysisResult ? `있음 (${documentAnalysisResult.length}자)` : '없음');
    if (documentAnalysisResult) {
      setLocalDocumentResult(documentAnalysisResult);
      console.log('🔧 로컬 상태로 복사 완료!');
    }
  }, [documentAnalysisResult]);

  useEffect(() => {
    console.log('🔍 MainContent - integratedAnalysisResult 변경 감지:', integratedAnalysisResult ? `있음 (${integratedAnalysisResult.length}자)` : '없음');
    if (integratedAnalysisResult) {
      setLocalIntegratedResult(integratedAnalysisResult);
      console.log('🔧 통합분석 로컬 상태로 복사 완료!');
    }
  }, [integratedAnalysisResult]);

  useEffect(() => {
    console.log('🔍 MainContent - forceUpdateCounter 변경 감지:', forceUpdateCounter);
  }, [forceUpdateCounter]);

  // 명시적 초기화 함수
  const clearLocalStates = () => {
    setLocalDocumentResult(null);
    setLocalIntegratedResult(null);
    console.log('🔄 MainContent - 로컬 상태 명시적 초기화 완료');
  };

  // 초기화 신호 감지
  useEffect(() => {
    if (clearSignal > 0) {
      clearLocalStates();
      console.log('🔄 MainContent - 초기화 신호 감지됨:', clearSignal);
    }
  }, [clearSignal]);

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
    <div className="flex-1 p-8 bg-gray-50 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
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
                ) : selectedJobFile ? (
                  <span className="flex items-center space-x-1">
                    <CheckCircle className="w-3 h-3 text-blue-600" />
                    <span>{selectedJobFile.replace('job_', '')}</span>
                    <span className="text-blue-600">(기존파일)</span>
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
                ) : selectedResumeFile ? (
                  <span className="flex items-center space-x-1">
                    <CheckCircle className="w-3 h-3 text-blue-600" />
                    <span>{selectedResumeFile.replace('resume_', '')}</span>
                    <span className="text-blue-600">(기존파일)</span>
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

      {/* Document Analysis Result */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center space-x-2">
          <BarChart3 className="w-6 h-6 text-blue-600" />
          <span>문서 분석 결과</span>
          {localDocumentResult && (
            <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
              ✅ 불러옴 ({localDocumentResult.length}자)
            </span>
          )}
        </h2>



        <div className="bg-gray-50 rounded-lg p-4 max-h-180 overflow-y-auto">
          {documentAnalysisError ? (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-700">❌ {documentAnalysisError}</p>
            </div>
          ) : localDocumentResult ? (
            <div className="prose prose-sm max-w-none text-sm text-gray-700 leading-relaxed">
              <ReactMarkdown>
                {localDocumentResult}
              </ReactMarkdown>
            </div>
          ) : (
            <div className="text-center py-4">
              <p className="text-sm text-gray-500 italic">
                채용공고와 이력서를 업로드한 후 사이드바에서 "문서 분석" 버튼을 클릭하면 결과가 여기에 표시됩니다
              </p>
              <div className="mt-2 text-xs text-gray-400">
                💡 기존 파일을 사용하려면 "기존 파일 목록 보기"를 클릭하세요
              </div>
            </div>
          )}
        </div>
      </div>

      {/* STT Result */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">면접 STT 결과</h2>
        <div className="bg-gray-50 rounded-lg p-4 max-h-180 overflow-y-auto">
          {sttResult ? (
            <div className="prose prose-sm max-w-none text-sm text-gray-700 leading-relaxed">
              <ReactMarkdown>
                {sttResult}
              </ReactMarkdown>
            </div>
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
        <div className="bg-gray-50 rounded-lg p-4 max-h-180 overflow-y-auto">
          {analysisResult ? (
            <div className="prose prose-sm max-w-none text-sm text-gray-700 leading-relaxed">
              <ReactMarkdown>
                {analysisResult}
              </ReactMarkdown>
            </div>
          ) : (
            <p className="text-sm text-gray-500 italic">
              {isAnalyzing ? 'AI가 면접 내용을 분석하고 있습니다...' : '파일을 업로드하고 분석을 시작하면 결과가 여기에 표시됩니다'}
            </p>
          )}
        </div>
      </div>

      {/* Integrated Analysis Result (2-Step Demo) */}
      {(localIntegratedResult || integratedAnalysisError) && (
        <div className="bg-white rounded-lg shadow-sm border border-blue-200 p-6 mb-6">
          <h2 className="text-xl font-semibold text-blue-800 mb-4 flex items-center space-x-2">
            <BarChart3 className="w-6 h-6 text-blue-600" />
            <span>🎯 최종 종합 평가 (2단계 통합 분석)</span>
          </h2>
          <div className="bg-blue-50 rounded-lg p-4 max-h-180 overflow-y-auto">
            {integratedAnalysisError ? (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-700">❌ {integratedAnalysisError}</p>
              </div>
            ) : localIntegratedResult ? (
              <div className="prose prose-sm max-w-none text-sm text-gray-700 leading-relaxed">
                <ReactMarkdown>
                  {localIntegratedResult}
                </ReactMarkdown>
              </div>
            ) : null}
          </div>
        </div>
      )}

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
            <div className="space-y-4 max-h-100 overflow-y-auto">
              {chatMessages.map((message, index) => (
                <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-3xl p-3 rounded-lg ${
                    message.role === 'user' 
                      ? 'bg-blue-100 text-blue-800' 
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {message.role === 'assistant' ? (
                      <div className="prose prose-sm max-w-none text-sm">
                        <ReactMarkdown>
                          {message.content}
                        </ReactMarkdown>
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

// Force module reload
export default MainContent;