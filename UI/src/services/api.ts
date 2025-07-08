// API 기본 설정 (Vite 프록시 사용)
const API_BASE_URL = '/api'; // Vite 프록시를 통해 백엔드로 전달

// 응답 타입 정의
export interface UploadResponse {
  status: 'success' | 'error';
  message: string;
  filename?: string;
}

export interface AnalysisResponse {
  status: 'success' | 'error';
  analysis?: string;
  message?: string;
}

export interface UploadAndAnalyzeResponse {
  status: 'success' | 'error';
  upload_results?: {
    resume_upload: UploadResponse;
    job_upload: UploadResponse;
  };
  indexer_result?: {
    status: string;
    message?: string;
  };
  index_info?: {
    old_index: string;
    new_index: string;
    index_changed: boolean;
  };
  indexing_status?: {
    resume_indexed: boolean;
    job_indexed: boolean;
  };
  analysis_result?: AnalysisResponse;
  message?: string;
}

export interface FileInfo {
  name: string;
  display_name: string;
  size: number;
  last_modified: string | null;
}

export interface FilesListResponse {
  status: 'success' | 'error';
  resume_files?: FileInfo[];
  job_files?: FileInfo[];
  total_files?: number;
  message?: string;
}

// 이력서 업로드
export const uploadResume = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/document/upload-resume`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
};

// 채용공고 업로드
export const uploadJob = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/document/upload-job`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
};

// 동시 업로드
export const uploadBothFiles = async (
  resumeFile: File, 
  jobFile: File
): Promise<UploadAndAnalyzeResponse> => {
  const formData = new FormData();
  formData.append('resume_file', resumeFile);
  formData.append('job_file', jobFile);

  const response = await fetch(`${API_BASE_URL}/document/upload-both`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
};

// 파일 분석
export const analyzeFiles = async (
  resumeFilename: string, 
  jobFilename: string
): Promise<AnalysisResponse> => {
  const response = await fetch(`${API_BASE_URL}/document/analyze-files`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      resume_filename: resumeFilename,
      job_filename: jobFilename,
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
};

// 업로드 + 분석 한 번에 (고속 모드)
export const uploadAndAnalyzeFast = async (
  resumeFile: File, 
  jobFile: File
): Promise<UploadAndAnalyzeResponse> => {
  const formData = new FormData();
  formData.append('resume_file', resumeFile);
  formData.append('job_file', jobFile);

  const response = await fetch(`${API_BASE_URL}/document/upload-and-analyze-fast`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
};

// 업로드 + 분석 한 번에 (일반 모드)
export const uploadAndAnalyze = async (
  resumeFile: File, 
  jobFile: File
): Promise<UploadAndAnalyzeResponse> => {
  const formData = new FormData();
  formData.append('resume_file', resumeFile);
  formData.append('job_file', jobFile);

  const response = await fetch(`${API_BASE_URL}/document/upload-and-analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
};

// 직접 텍스트 분석
export const analyzeText = async (
  resumeText: string, 
  jobText: string
): Promise<AnalysisResponse> => {
  const response = await fetch(`${API_BASE_URL}/document/analyze-text`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      resume_text: resumeText,
      job_posting_text: jobText,
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
}; 

// 파일 목록 조회
export const getFilesList = async (): Promise<FilesListResponse> => {
  const response = await fetch(`${API_BASE_URL}/document/files-list`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
}; 

// 2단계 시연용: 통합 분석
export const integratedAnalysis = async (
  documentAnalysis: string,
  interviewStt: string,
  resumeFilename?: string,
  jobFilename?: string
): Promise<{
  status: 'success' | 'error';
  analysis_type?: string;
  integrated_analysis?: string;
  message?: string;
}> => {
  const response = await fetch(`${API_BASE_URL}/document/integrated-analysis`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      document_analysis: documentAnalysis,
      interview_stt: interviewStt,
      resume_filename: resumeFilename || '',
      job_filename: jobFilename || ''
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
}; 

// ========== 면접 분석 API ==========

// 면접 업로드 + STT 한 번에
export const uploadAndTranscribeInterview = async (file: File): Promise<{
  status: 'success' | 'error';
  upload_result?: UploadResponse;
  transcribe_result?: any;
  filename?: string;
  transcription?: string;
  message?: string;
}> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/interview/upload-and-transcribe`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
};

// 빠른 면접 분석 (기존 STT 결과 활용)
export const quickInterviewAnalysis = async (
  sttResult: string,
  jobPostingContent?: string,
  resumeContent?: string
): Promise<{
  status: 'success' | 'error';
  analysis?: string;
  text_length?: number;
  message?: string;
}> => {
  const response = await fetch(`${API_BASE_URL}/interview/quick-analysis`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      stt_result: sttResult,
      job_posting_content: jobPostingContent || '',
      resume_content: resumeContent || ''
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
}; 

// 면접 녹음 파일 목록 조회
export const getInterviewFiles = async (): Promise<{
  status: 'success' | 'error';
  interview_files?: FileInfo[];
  total_files?: number;
  message?: string;
}> => {
  const response = await fetch(`${API_BASE_URL}/interview/audio-files`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
}; 