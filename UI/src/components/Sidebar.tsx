import React, { useState, useEffect } from 'react';
import { Send, FileText, User, Mic, ChevronLeft, ChevronRight, RefreshCw, BarChart3, List, X } from 'lucide-react';
import FileUploader from './FileUploader';
import { uploadAndAnalyze, uploadAndAnalyzeFast, uploadBothFiles, analyzeFiles, getFilesList, integratedAnalysis, uploadAndTranscribeInterview, quickInterviewAnalysis, getInterviewFiles } from '../services/api';
import type { UploadAndAnalyzeResponse, AnalysisResponse, FilesListResponse, FileInfo } from '../services/api';

interface SidebarProps {
  jobPostingFile?: File;
  resumeFile?: File;
  interviewFile?: File;
  onJobPostingUpload: (file: File) => void;
  onResumeUpload: (file: File) => void;
  onInterviewUpload: (file: File) => void;
  onRemoveJobPosting: () => void;
  onRemoveResume: () => void;
  onRemoveInterview: () => void;
  onStartAnalysis: () => void;
  isAnalyzing: boolean;
  isOpen: boolean;
  onToggle: () => void;
  onDocumentAnalysisUpdate: (result: string | null, error: string | null) => void;
  selectedResumeFile: string | null;
  selectedJobFile: string | null;
  selectedInterviewFile: string | null;
  onSelectedResumeChange: (filename: string | null) => void;
  onSelectedJobChange: (filename: string | null) => void;
  onSelectedInterviewChange: (filename: string | null) => void;
  onIntegratedAnalysisUpdate: (result: string | null, error: string | null) => void;
  sttResult: string;
  documentAnalysisResult: string | null;
  onResetAll: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  jobPostingFile,
  resumeFile,
  interviewFile,
  onJobPostingUpload,
  onResumeUpload,
  onInterviewUpload,
  onRemoveJobPosting,
  onRemoveResume,
  onRemoveInterview,
  onStartAnalysis,
  isAnalyzing,
  isOpen,
  onToggle,
  onDocumentAnalysisUpdate,
  selectedResumeFile,
  selectedJobFile,
  selectedInterviewFile,
  onSelectedResumeChange,
  onSelectedJobChange,
  onSelectedInterviewChange,
  onIntegratedAnalysisUpdate,
  sttResult,
  documentAnalysisResult,
  onResetAll
}) => {
  // 문서 분석 상태 관리
  const [isDocumentAnalyzing, setIsDocumentAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<string | null>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [analysisProgress, setAnalysisProgress] = useState<string>('');
  const [fastMode, setFastMode] = useState(true); // 기본값: 고속 모드
  
  // 2단계 통합 분석 상태 관리
  const [isIntegratedAnalyzing, setIsIntegratedAnalyzing] = useState(false);
  
  // 파일 목록 상태 관리
  const [isLoadingFiles, setIsLoadingFiles] = useState(false);
  const [showFilesList, setShowFilesList] = useState(false);
  const [availableFiles, setAvailableFiles] = useState<{
    resume_files: FileInfo[];
    job_files: FileInfo[];
    interview_files: FileInfo[];
  }>({
    resume_files: [],
    job_files: [],
    interview_files: []
  });

  // 분석 모드 설정 토글 상태
  const [showAnalysisMode, setShowAnalysisMode] = useState(false);

  const canStartAnalysis = jobPostingFile && resumeFile && interviewFile;
  const canAnalyzeDocuments = jobPostingFile && resumeFile;
  const canAnalyzeSelected = selectedResumeFile && selectedJobFile;
  const canAnalyzeSelectedAll = selectedResumeFile && selectedJobFile && selectedInterviewFile;
  const canIntegratedAnalysis = (documentAnalysisResult || analysisResult) && sttResult;

  // 분석 결과가 변경될 때마다 부모 컴포넌트에게 알림
  useEffect(() => {
    onDocumentAnalysisUpdate(analysisResult, analysisError);
  }, [analysisResult, analysisError, onDocumentAnalysisUpdate]);

  // 파일 목록 불러오기
  const loadFilesList = async () => {
    setIsLoadingFiles(true);
    try {
      // 문서 파일 목록 조회
      const documentResult: FilesListResponse = await getFilesList();
      
      // 면접 파일 목록 조회
      const interviewResult = await getInterviewFiles();
      
      if (documentResult.status === 'success') {
        setAvailableFiles({
          resume_files: documentResult.resume_files || [],
          job_files: documentResult.job_files || [],
          interview_files: interviewResult.status === 'success' ? (interviewResult.interview_files || []) : []
        });
        setShowFilesList(true);
      } else {
        console.error('파일 목록 조회 실패:', documentResult.message);
      }
    } catch (error) {
      console.error('파일 목록 조회 오류:', error);
    } finally {
      setIsLoadingFiles(false);
    }
  };

  // 선택한 파일들로 분석
  const handleAnalyzeSelectedFiles = async () => {
    if (!selectedResumeFile || !selectedJobFile) {
      setAnalysisError('이력서와 채용공고 파일을 선택해주세요.');
      return;
    }

    setIsDocumentAnalyzing(true);
    setAnalysisError(null);
    setAnalysisResult(null);

    try {
      console.log('선택한 파일들로 분석 시작...');
      const result: AnalysisResponse = await analyzeFiles(
        selectedResumeFile.replace('resume_', ''),
        selectedJobFile.replace('job_', '')
      );
      
      if (result.status === 'success' && result.analysis) {
        setAnalysisResult(result.analysis);
        console.log('선택한 파일들 분석 완료!');
      } else {
        setAnalysisError(result.message || '선택한 파일들 분석에 실패했습니다.');
      }
    } catch (error) {
      console.error('선택한 파일들 분석 오류:', error);
      setAnalysisError(`선택한 파일들 분석 중 오류가 발생했습니다: ${error}`);
    } finally {
      setIsDocumentAnalyzing(false);
    }
  };

  // 기존 파일들로 전체 분석 (문서 + 면접)
  const handleAnalyzeSelectedAllFiles = async () => {
    if (!selectedResumeFile || !selectedJobFile || !selectedInterviewFile) {
      setAnalysisError('이력서, 채용공고, 면접 녹음 파일을 모두 선택해주세요.');
      return;
    }

    setIsDocumentAnalyzing(true);
    setAnalysisError(null);
    setAnalysisResult(null);

    try {
      console.log('🚀 기존 파일들로 전체 분석 시작...');
      
      // 1단계: 문서 분석
      console.log('📄 1단계: 문서 분석 중...');
      const documentResult: AnalysisResponse = await analyzeFiles(
        selectedResumeFile.replace('resume_', ''),
        selectedJobFile.replace('job_', '')
      );
      
      if (documentResult.status !== 'success' || !documentResult.analysis) {
        setAnalysisError(documentResult.message || '문서 분석에 실패했습니다.');
        return;
      }

      // 문서 분석 결과 업데이트
      setAnalysisResult(documentResult.analysis);
      onDocumentAnalysisUpdate(documentResult.analysis, null);

      // 2단계: 면접 STT (기존 파일은 이미 텍스트로 변환되었다고 가정)
      console.log('🎤 2단계: 면접 내용 분석 중...');
      // TODO: 기존 면접 파일의 STT 결과 가져오기 또는 STT 처리
      // 현재는 임시로 빈 문자열 사용
      const mockSttResult = "면접 내용이 여기에 표시됩니다. (기존 파일 STT 기능 구현 필요)";
      
      // 면접 분석
      const interviewAnalysisResult = await quickInterviewAnalysis(
        mockSttResult,
        selectedJobFile ? "채용공고 내용" : undefined,
        selectedResumeFile ? "이력서 내용" : undefined
      );
      
      // 3단계: 통합 분석
      console.log('🎯 3단계: 통합 분석 중...');
      const integratedResult = await integratedAnalysis(
        documentResult.analysis,
        mockSttResult,
        selectedResumeFile,
        selectedJobFile
      );
      
      if (integratedResult.status === 'success' && integratedResult.integrated_analysis) {
        onIntegratedAnalysisUpdate(integratedResult.integrated_analysis, null);
        console.log('✅ 기존 파일들로 전체 분석 완료!');
      } else {
        console.log('⚠️ 통합 분석은 실패했지만 문서 분석은 완료됨');
      }
      
    } catch (error) {
      console.error('❌ 전체 분석 오류:', error);
      setAnalysisError(`전체 분석 중 오류가 발생했습니다: ${error}`);
    } finally {
      setIsDocumentAnalyzing(false);
    }
  };

  // 업로드된 파일들로 분석 (시연용 최적화)
  const handleDocumentAnalysis = async () => {
    if (!jobPostingFile || !resumeFile) {
      setAnalysisError('이력서와 채용공고 파일을 모두 업로드해주세요.');
      return;
    }

    setIsDocumentAnalyzing(true);
    setAnalysisError(null);
    setAnalysisResult(null);
    setAnalysisProgress('📤 1단계: 파일 업로드 중...');

    try {
      console.log('🚀 시연용 업로드+분석 시작...');
      
      // 진행 상황 표시를 위한 지연
      await new Promise(resolve => setTimeout(resolve, 500));
      setAnalysisProgress('⚡ 2단계: 인덱서 실행 중...');
      
      await new Promise(resolve => setTimeout(resolve, 500));
      setAnalysisProgress('🔍 3단계: 최신 인덱스 재발견 중...');
      
      await new Promise(resolve => setTimeout(resolve, 500));
      setAnalysisProgress('⏳ 4단계: 인덱싱 완료 대기 중...');
      
      const result: UploadAndAnalyzeResponse = fastMode 
        ? await uploadAndAnalyzeFast(resumeFile, jobPostingFile)
        : await uploadAndAnalyze(resumeFile, jobPostingFile);
      
      setAnalysisProgress('📊 5단계: 분석 실행 중...');
      
      // 상세 진행 상황 로그
      console.log('📊 분석 결과:', result);
      
      if (result.indexer_result) {
        console.log('⚡ 인덱서 실행 결과:', result.indexer_result.status);
      }
      
      if (result.index_info) {
        console.log(`🔍 인덱스 정보: ${result.index_info.old_index} → ${result.index_info.new_index}`);
        if (result.index_info.index_changed) {
          console.log('✅ 새로운 인덱스가 발견되었습니다!');
        }
      }
      
      if (result.indexing_status) {
        console.log(`📋 인덱싱 상태 - 이력서: ${result.indexing_status.resume_indexed}, 채용공고: ${result.indexing_status.job_indexed}`);
      }
      
      if (result.status === 'success' && result.analysis_result?.analysis) {
        setAnalysisProgress('✅ 분석 완료!');
        setAnalysisResult(result.analysis_result.analysis);
        console.log('✅ 시연용 분석 완료!');
        
        // 인덱싱 상태 정보를 사용자에게 표시
        let statusMessage = '';
        if (result.indexing_status && (!result.indexing_status.resume_indexed || !result.indexing_status.job_indexed)) {
          statusMessage = '\n\n⚠️ 일부 파일의 인덱싱이 완료되지 않았지만 분석을 진행했습니다.';
        }
        
        if (result.index_info?.index_changed) {
          statusMessage += '\n\n✅ 새로운 인덱스가 자동으로 감지되었습니다.';
        }
        
        if (statusMessage) {
          setAnalysisResult(result.analysis_result.analysis + statusMessage);
        }
        
      } else {
        setAnalysisError(result.message || '업로드된 파일들 분석에 실패했습니다.');
      }
    } catch (error) {
      console.error('❌ 시연용 분석 오류:', error);
      setAnalysisError(`업로드된 파일들 분석 중 오류가 발생했습니다: ${error}`);
    } finally {
      setIsDocumentAnalyzing(false);
      setAnalysisProgress('');
    }
  };

  // 2단계 통합 분석 핸들러
  const handleIntegratedAnalysis = async () => {
    if (!canIntegratedAnalysis) {
      onIntegratedAnalysisUpdate(null, '1단계 문서 분석과 면접 STT 결과가 모두 필요합니다.');
      return;
    }

    setIsIntegratedAnalyzing(true);
    onIntegratedAnalysisUpdate(null, null);

    try {
      console.log('🔄 2단계: 통합 분석 시작...');
      
      // 문서 분석 결과 우선순위: documentAnalysisResult > analysisResult
      const docResult = documentAnalysisResult || analysisResult || '';
      
      const result = await integratedAnalysis(
        docResult,
        sttResult,
        resumeFile?.name || selectedResumeFile || '',
        jobPostingFile?.name || selectedJobFile || ''
      );
      
      if (result.status === 'success' && result.integrated_analysis) {
        onIntegratedAnalysisUpdate(result.integrated_analysis, null);
        console.log('✅ 2단계 통합 분석 완료!');
      } else {
        onIntegratedAnalysisUpdate(null, result.message || '통합 분석에 실패했습니다.');
      }
    } catch (error) {
      console.error('❌ 통합 분석 오류:', error);
      onIntegratedAnalysisUpdate(null, `통합 분석 중 오류가 발생했습니다: ${error}`);
    } finally {
      setIsIntegratedAnalyzing(false);
    }
  };

  // 분석 결과 초기화
  const handleResetAnalysis = () => {
    setAnalysisResult(null);
    setAnalysisError(null);
  };

  // 전체 초기화 (파일 + 분석 결과) - 이제 App.tsx에서 처리
  const handleResetAll = () => {
    // 부모 컴포넌트의 초기화 함수 호출
    onResetAll();
    
    // 로컬 상태 초기화
    setAnalysisResult(null);
    setAnalysisError(null);
    setShowFilesList(false);
  };

  return (
    <div className={`${isOpen ? 'w-96' : 'w-16'} bg-white border-r border-gray-200 flex flex-col h-screen transition-all duration-300 ease-in-out relative`}>
      {/* 토글 버튼 */}
      <button
        onClick={onToggle}
        className="absolute -right-3 top-6 z-10 bg-white border border-gray-200 rounded-full p-1.5 shadow-md hover:shadow-lg transition-shadow duration-200"
      >
        {isOpen ? (
          <ChevronLeft className="w-4 h-4 text-gray-600" />
        ) : (
          <ChevronRight className="w-4 h-4 text-gray-600" />
        )}
      </button>

      {/* 사이드바 내용 */}
      <div className={`${isOpen ? 'p-6' : 'p-4'} flex flex-col h-full ${isOpen ? 'opacity-100' : 'opacity-0'} transition-opacity duration-300 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100`}>
        <div className="mb-6">
          <h2 className="text-xl font-bold text-gray-800 mb-2">파일 관리</h2>
          <p className="text-sm text-gray-600">
            새로 업로드하거나 기존 파일을 선택하세요
          </p>
        </div>

        {/* 기존 파일 불러오기 버튼 */}
        <div className="mb-6">
          <button
            onClick={loadFilesList}
            disabled={isLoadingFiles}
            className="w-full flex items-center justify-center space-x-2 py-2 px-4 rounded-lg font-medium bg-sky-100 text-sky-700 hover:bg-sky-200 transition-colors"
          >
            <List className="w-4 h-4" />
            <span>
              {isLoadingFiles ? '불러오는 중...' : '기존 파일 목록 보기'}
            </span>
          </button>
        </div>

        {/* 기존 파일 선택 영역 */}
        {showFilesList && (
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-gray-700">기존 파일 선택</h3>
              <button
                onClick={() => setShowFilesList(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            
            {/* 이력서 파일 선택 */}
            <div className="mb-3">
              <label className="block text-xs font-medium text-gray-600 mb-1">이력서 파일</label>
              <select
                value={selectedResumeFile || ''}
                onChange={(e) => onSelectedResumeChange(e.target.value || null)}
                className="w-full text-sm border border-gray-300 rounded px-2 py-1"
              >
                <option value="">선택하세요</option>
                {availableFiles.resume_files.map((file) => (
                  <option key={file.name} value={file.name}>
                    {file.display_name}
                  </option>
                ))}
              </select>
            </div>

            {/* 채용공고 파일 선택 */}
            <div className="mb-3">
              <label className="block text-xs font-medium text-gray-600 mb-1">채용공고 파일</label>
              <select
                value={selectedJobFile || ''}
                onChange={(e) => onSelectedJobChange(e.target.value || null)}
                className="w-full text-sm border border-gray-300 rounded px-2 py-1"
              >
                <option value="">선택하세요</option>
                {availableFiles.job_files.map((file) => (
                  <option key={file.name} value={file.name}>
                    {file.display_name}
                  </option>
                ))}
              </select>
            </div>

            {/* 면접 녹음 파일 선택 */}
            <div className="mb-3">
              <label className="block text-xs font-medium text-gray-600 mb-1">면접 녹음 파일</label>
              <select
                value={selectedInterviewFile || ''}
                onChange={(e) => onSelectedInterviewChange(e.target.value || null)}
                className="w-full text-sm border border-gray-300 rounded px-2 py-1"
              >
                <option value="">선택하세요</option>
                {availableFiles.interview_files.map((file) => (
                  <option key={file.name} value={file.name}>
                    {file.display_name}
                  </option>
                ))}
              </select>
            </div>

            {/* 선택한 파일들로 분석 버튼 */}
            <div className="space-y-2">
              <button
                onClick={handleAnalyzeSelectedFiles}
                disabled={!canAnalyzeSelected || isDocumentAnalyzing}
                className={`w-full flex items-center justify-center space-x-2 py-2 px-3 rounded-lg font-medium text-sm transition-all
                  ${canAnalyzeSelected && !isDocumentAnalyzing
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                  }`}
              >
                <BarChart3 className="w-4 h-4" />
                <span>
                  {isDocumentAnalyzing ? '분석 중...' : '문서만 분석'}
                </span>
              </button>

              {/* 전체 분석 버튼 (문서 + 면접) */}
              <button
                onClick={handleAnalyzeSelectedAllFiles}
                disabled={!canAnalyzeSelectedAll || isDocumentAnalyzing}
                className={`w-full flex items-center justify-center space-x-2 py-2 px-3 rounded-lg font-medium text-sm transition-all
                  ${canAnalyzeSelectedAll && !isDocumentAnalyzing
                    ? 'bg-purple-600 text-white hover:bg-purple-700'
                    : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                  }`}
              >
                <Mic className="w-4 h-4" />
                <span>
                  {isDocumentAnalyzing ? '분석 중...' : '🎯 전체 분석 (문서+면접)'}
                </span>
              </button>
            </div>
          </div>
        )}

          <div className="space-y-6">
            {/* 채용공고 업로드 */}
            <div className="flex items-center space-x-2 mb-3">
              <FileText className="w-5 h-5 text-blue-600" />
              <span className="text-sm font-medium text-gray-700">채용공고 업로드</span>
            </div>
            <FileUploader
              title="채용공고 업로드"
              allowedTypes={['pdf', 'doc', 'docx']}
              fileTypeLabel="PDF, DOC, DOCX"
              onFileUpload={onJobPostingUpload}
              uploadedFile={jobPostingFile}
              onRemoveFile={onRemoveJobPosting}
            />

            {/* 이력서 업로드 */}
            <div className="flex items-center space-x-2 mb-3">
              <User className="w-5 h-5 text-green-600" />
              <span className="text-sm font-medium text-gray-700">이력서 업로드</span>
            </div>
            <FileUploader
              title="이력서 업로드"
              allowedTypes={['pdf', 'doc', 'docx']}
              fileTypeLabel="PDF, DOC, DOCX"
              onFileUpload={onResumeUpload}
              uploadedFile={resumeFile}
              onRemoveFile={onRemoveResume}
            />

            {/* 면접 녹음 업로드 */}
            <div className="flex items-center space-x-2 mb-3">
              <Mic className="w-5 h-5 text-purple-600" />
              <span className="text-sm font-medium text-gray-700">면접 녹음</span>
            </div>
            <FileUploader
              title="면접 녹음 파일 업로드"
              allowedTypes={['mp3', 'wav']}
              fileTypeLabel="MP3, WAV"
              onFileUpload={onInterviewUpload}
              uploadedFile={interviewFile}
              onRemoveFile={onRemoveInterview}
            />
          </div>

        {/* 버튼 섹션 */}
        <div className="mt-8 pt-6 border-t border-gray-200 space-y-3">
          {/* 분석 모드 선택 토글 */}
          <div className="mb-4">
            <button
              onClick={() => setShowAnalysisMode(!showAnalysisMode)}
              className="w-full flex items-center justify-between p-3 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
            >
              <div className="flex items-center space-x-2">
                <span className="text-sm font-semibold text-blue-800">
                  📊 분석 설정
                </span>
                <span className="text-xs text-blue-600">
                  (성능 최적화 옵션)
                </span>
              </div>
              <ChevronRight className={`w-4 h-4 text-blue-600 transform transition-transform ${showAnalysisMode ? 'rotate-90' : ''}`} />
            </button>
            
            {showAnalysisMode && (
              <div className="mt-2 p-3 bg-white border border-blue-200 rounded-lg space-y-2">
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="radio"
                    name="analysisMode"
                    checked={fastMode}
                    onChange={() => setFastMode(true)}
                    className="text-blue-600"
                  />
                  <div className="flex-1">
                    <span className="text-sm text-blue-700 font-medium">⚡ 빠른 분석</span>
                    <p className="text-xs text-blue-600">스마트 청킹 + 10초 인덱싱</p>
                    <p className="text-xs text-blue-500">• 핵심 키워드 중심 벡터화</p>
                    <p className="text-xs text-blue-500">• 실시간 응답용 최적화</p>
                  </div>
                </label>
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="radio"
                    name="analysisMode"
                    checked={!fastMode}
                    onChange={() => setFastMode(false)}
                    className="text-blue-600"
                  />
                  <div className="flex-1">
                    <span className="text-sm text-blue-700 font-medium">🔄 정밀 분석</span>
                    <p className="text-xs text-blue-600">딥 청킹 + 30초 완전 인덱싱</p>
                    <p className="text-xs text-blue-500">• 문맥/의미 완전 분석</p>
                    <p className="text-xs text-blue-500">• 미묘한 표현까지 캐치</p>
                  </div>
                </label>
              </div>
            )}
          </div>

          {/* 업로드된 파일들 분석 버튼 */}
          <button
            onClick={handleDocumentAnalysis}
            disabled={!canAnalyzeDocuments || isDocumentAnalyzing}
            className={`w-full flex flex-col items-center justify-center space-y-1 py-3 px-4 rounded-lg font-medium transition-all
              ${canAnalyzeDocuments && !isDocumentAnalyzing
                ? 'bg-green-600 text-white hover:bg-green-700 transform hover:scale-105'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
              }`}
          >
            <div className="flex items-center space-x-2">
              <BarChart3 className="w-5 h-5" />
              <span>
                {isDocumentAnalyzing 
                  ? (fastMode ? '⚡ 빠른 분석 중...' : '🔄 정밀 분석 중...') 
                  : (fastMode ? '⚡ 빠른 분석' : '🔄 정밀 분석')
                }
              </span>
            </div>
            {analysisProgress && (
              <div className="text-xs opacity-90 text-center">
                {analysisProgress}
              </div>
            )}
          </button>

          {/* 분석 결과 초기화 버튼 */}
          {(analysisResult || analysisError) && (
            <button
              onClick={handleResetAnalysis}
              className="w-full flex items-center justify-center space-x-2 py-2 px-4 rounded-lg font-medium bg-gray-100 text-gray-700 hover:bg-gray-200 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              <span>분석 결과 초기화</span>
            </button>
          )}

          {/* 2단계 통합 분석 버튼 */}
          <button
            onClick={handleIntegratedAnalysis}
            disabled={!canIntegratedAnalysis || isIntegratedAnalyzing}
            className={`w-full flex items-center justify-center space-x-2 py-3 px-4 rounded-lg font-medium transition-all border-2
              ${canIntegratedAnalysis && !isIntegratedAnalyzing
                ? 'bg-blue-600 text-white border-blue-600 hover:bg-blue-700 transform hover:scale-105'
                : 'bg-gray-200 text-gray-400 border-gray-300 cursor-not-allowed'
              }`}
          >
            <BarChart3 className="w-5 h-5" />
            <span>
              {isIntegratedAnalyzing ? '🔄 통합 분석 중...' : '🎯 2단계: 최종 종합 평가'}
            </span>
          </button>

          {/* 전체 초기화 버튼 */}
          <button
            onClick={handleResetAll}
            className="w-full flex items-center justify-center space-x-2 py-2 px-4 rounded-lg font-medium bg-red-100 text-red-700 hover:bg-red-200 transition-colors"
          >
            <X className="w-4 h-4" />
            <span>전체 초기화</span>
          </button>
        </div>


      </div>

      {/* 닫혔을 때 표시할 아이콘들 */}
      {!isOpen && (
        <div className="p-4 flex flex-col items-center space-y-4 mt-16">
          <div className="p-2 rounded-lg bg-blue-50">
            <FileText className="w-6 h-6 text-blue-600" />
          </div>
          <div className="p-2 rounded-lg bg-green-50">
            <User className="w-6 h-6 text-green-600" />
          </div>
          <div className="p-2 rounded-lg bg-purple-50">
            <Mic className="w-6 h-6 text-purple-600" />
          </div>
        </div>
      )}
    </div>
  );
};

export default Sidebar;