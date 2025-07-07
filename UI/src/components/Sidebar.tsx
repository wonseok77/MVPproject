import React from 'react';
import { Send, FileText, User, Mic, ChevronLeft, ChevronRight } from 'lucide-react';
import FileUploader from './FileUploader';

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
  const canStartAnalysis = jobPostingFile && resumeFile && interviewFile;

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
      <div className={`${isOpen ? 'p-6' : 'p-4'} flex flex-col h-full ${isOpen ? 'opacity-100' : 'opacity-0'} transition-opacity duration-300`}>
        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-800 mb-2">파일 업로드</h2>
          <p className="text-sm text-gray-600">
            분석에 필요한 파일들을 업로드해주세요
          </p>
        </div>

        <div className="flex-1 overflow-y-auto">
          <div className="space-y-6">
            <div className="flex items-center space-x-2 mb-3">
              <FileText className="w-5 h-5 text-blue-600" />
              <span className="text-sm font-medium text-gray-700">채용공고</span>
            </div>
            <FileUploader
              title="채용공고 업로드"
              allowedTypes={['pdf', 'doc', 'docx']}
              fileTypeLabel="PDF, DOC, DOCX"
              onFileUpload={onJobPostingUpload}
              uploadedFile={jobPostingFile}
              onRemoveFile={onRemoveJobPosting}
            />

            <div className="flex items-center space-x-2 mb-3">
              <User className="w-5 h-5 text-green-600" />
              <span className="text-sm font-medium text-gray-700">이력서</span>
            </div>
            <FileUploader
              title="이력서 업로드"
              allowedTypes={['pdf', 'doc', 'docx']}
              fileTypeLabel="PDF, DOC, DOCX"
              onFileUpload={onResumeUpload}
              uploadedFile={resumeFile}
              onRemoveFile={onRemoveResume}
            />

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
        </div>

        <div className="mt-8 pt-6 border-t border-gray-200">
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
              {isAnalyzing ? '분석 중...' : '전송 및 분석 시작'}
            </span>
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