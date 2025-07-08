import React, { useState, useEffect } from 'react';
import { Send, FileText, User, Mic, ChevronLeft, ChevronRight, RefreshCw, BarChart3, List, X } from 'lucide-react';
import FileUploader from './FileUploader';
import { uploadAndAnalyze, uploadBothFiles, analyzeFiles, getFilesList } from '../services/api';
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
  onToggle
}) => {
  // 문서 분석 상태 관리
  const [isDocumentAnalyzing, setIsDocumentAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<string | null>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  
  // 파일 목록 상태 관리
  const [isLoadingFiles, setIsLoadingFiles] = useState(false);
  const [showFilesList, setShowFilesList] = useState(false);
  const [availableFiles, setAvailableFiles] = useState<{
    resume_files: FileInfo[];
    job_files: FileInfo[];
  }>({
    resume_files: [],
    job_files: []
  });
  const [selectedResumeFile, setSelectedResumeFile] = useState<string | null>(null);
  const [selectedJobFile, setSelectedJobFile] = useState<string | null>(null);

  const canStartAnalysis = jobPostingFile && resumeFile && interviewFile;
  const canAnalyzeDocuments = jobPostingFile && resumeFile;
  const canAnalyzeSelected = selectedResumeFile && selectedJobFile;

  // 파일 목록 불러오기
  const loadFilesList = async () => {
    setIsLoadingFiles(true);
    try {
      const result: FilesListResponse = await getFilesList();
      if (result.status === 'success') {
        setAvailableFiles({
          resume_files: result.resume_files || [],
          job_files: result.job_files || []
        });
        setShowFilesList(true);
      } else {
        console.error('파일 목록 조회 실패:', result.message);
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

  // 업로드된 파일들로 분석 (기존 기능)
  const handleDocumentAnalysis = async () => {
    if (!jobPostingFile || !resumeFile) {
      setAnalysisError('이력서와 채용공고 파일을 모두 업로드해주세요.');
      return;
    }

    setIsDocumentAnalyzing(true);
    setAnalysisError(null);
    setAnalysisResult(null);

    try {
      console.log('업로드된 파일들로 분석 시작...');
      const result: UploadAndAnalyzeResponse = await uploadAndAnalyze(resumeFile, jobPostingFile);
      
      if (result.status === 'success' && result.analysis_result?.analysis) {
        setAnalysisResult(result.analysis_result.analysis);
        console.log('업로드된 파일들 분석 완료!');
      } else {
        setAnalysisError(result.message || '업로드된 파일들 분석에 실패했습니다.');
      }
    } catch (error) {
      console.error('업로드된 파일들 분석 오류:', error);
      setAnalysisError(`업로드된 파일들 분석 중 오류가 발생했습니다: ${error}`);
    } finally {
      setIsDocumentAnalyzing(false);
    }
  };

  // 분석 결과 초기화
  const handleResetAnalysis = () => {
    setAnalysisResult(null);
    setAnalysisError(null);
  };

  // 전체 초기화 (파일 + 분석 결과)
  const handleResetAll = () => {
    // 업로드된 파일들 제거
    onRemoveJobPosting();
    onRemoveResume();
    onRemoveInterview();
    
    // 선택한 파일들 제거
    setSelectedResumeFile(null);
    setSelectedJobFile(null);
    
    // 분석 결과 초기화
    setAnalysisResult(null);
    setAnalysisError(null);
    
    // 파일 목록 숨기기
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
                onChange={(e) => setSelectedResumeFile(e.target.value || null)}
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
                onChange={(e) => setSelectedJobFile(e.target.value || null)}
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

            {/* 선택한 파일들로 분석 버튼 */}
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
                {isDocumentAnalyzing ? '분석 중...' : '선택한 파일들 분석'}
              </span>
            </button>
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
          {/* 업로드된 파일들 분석 버튼 */}
          <button
            onClick={handleDocumentAnalysis}
            disabled={!canAnalyzeDocuments || isDocumentAnalyzing}
            className={`w-full flex items-center justify-center space-x-2 py-3 px-4 rounded-lg font-medium transition-all
              ${canAnalyzeDocuments && !isDocumentAnalyzing
                ? 'bg-green-600 text-white hover:bg-green-700 transform hover:scale-105'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
              }`}
          >
            <BarChart3 className="w-5 h-5" />
            <span>
              {isDocumentAnalyzing ? '분석 중...' : '업로드된 파일들 분석'}
            </span>
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

          {/* 전체 초기화 버튼 */}
          <button
            onClick={handleResetAll}
            className="w-full flex items-center justify-center space-x-2 py-2 px-4 rounded-lg font-medium bg-red-100 text-red-700 hover:bg-red-200 transition-colors"
          >
            <X className="w-4 h-4" />
            <span>전체 초기화</span>
          </button>

          {/* 전체 분석 버튼 */}
          <button
            onClick={onStartAnalysis}
            disabled={!canStartAnalysis || isAnalyzing}
            className={`w-full flex items-center justify-center space-x-2 py-3 px-4 rounded-lg font-medium transition-all
              ${canStartAnalysis && !isAnalyzing
                ? 'bg-blue-600 text-white hover:bg-blue-700 transform hover:scale-105'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
              }`}
          >
            <Send className="w-5 h-5" />
            <span>
              {isAnalyzing ? '전체 분석 중...' : '전체 분석 시작'}
            </span>
          </button>
        </div>

        {/* 분석 결과 표시 */}
        {analysisError && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-700">❌ {analysisError}</p>
          </div>
        )}

        {analysisResult && (
          <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg max-h-40 overflow-y-auto">
            <h4 className="text-sm font-semibold text-green-800 mb-2">
              ✅ 문서 분석 결과
            </h4>
            <div className="text-xs text-green-700 whitespace-pre-wrap">
              {analysisResult}
            </div>
          </div>
        )}
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