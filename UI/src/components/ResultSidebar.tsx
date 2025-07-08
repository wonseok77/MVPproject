import React, { useState, useEffect } from 'react';
import { ChevronLeftIcon, ChevronRightIcon, BookmarkIcon, ClockIcon, DocumentTextIcon, TrashIcon } from '@heroicons/react/24/outline';

interface SavedResult {
  filename: string;
  metadata: {
    saved_at: string;
    resume_file: string;
    job_file: string;
    analysis_type: string;
    timestamp?: string;
    file_size?: number;
  };
  results: {
    document_analysis?: string;
    interview_stt?: string;
    integrated_analysis?: string;
  };
}

interface ResultSidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  onSaveResult: (data: any) => void;
  onLoadResult: (result: SavedResult) => void;
  currentResults: {
    documentAnalysis?: string;
    integratedAnalysis?: string;
    sttResult?: string;
    resumeFile?: string;
    jobFile?: string;
  };
}

const ResultSidebar: React.FC<ResultSidebarProps> = ({
  isOpen,
  onToggle,
  onSaveResult,
  onLoadResult,
  currentResults
}) => {
  const [savedResults, setSavedResults] = useState<SavedResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 저장된 결과 목록 불러오기
  const fetchSavedResults = async () => {
    try {
      setLoading(true);
      console.log('📋 저장된 결과 목록 조회 시작...');
      
      const response = await fetch('/api/document/get-saved-results');
      console.log('🔍 API 응답:', response.status, response.statusText);
      
      if (response.ok) {
        const data = await response.json();
        console.log('📊 받은 데이터:', data);
        setSavedResults(data.results || []);
        setError(null);
      } else {
        const errorText = await response.text();
        console.error('❌ API 오류:', response.status, errorText);
        setError(`API 오류: ${response.status} ${response.statusText}`);
      }
    } catch (err) {
      console.error('❌ 네트워크 오류:', err);
      setError(`네트워크 오류: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setLoading(false);
    }
  };

  // 컴포넌트 마운트 시 저장된 결과 불러오기
  useEffect(() => {
    if (isOpen) {
      fetchSavedResults();
    }
  }, [isOpen]);

  // 현재 결과 저장
  const handleSaveCurrentResult = async () => {
    if (!currentResults.documentAnalysis && !currentResults.integratedAnalysis) {
      setError('저장할 분석 결과가 없습니다.');
      return;
    }

    try {
      setLoading(true);
      const saveData = {
        metadata: {
          saved_at: new Date().toISOString(),
          resume_file: currentResults.resumeFile || '',
          job_file: currentResults.jobFile || '',
          analysis_type: currentResults.integratedAnalysis ? 'integrated' : 'document'
        },
        results: {
          document_analysis: currentResults.documentAnalysis || '',
          interview_stt: currentResults.sttResult || '',
          integrated_analysis: currentResults.integratedAnalysis || ''
        }
      };
      
      console.log('💾 저장할 데이터:', JSON.stringify(saveData, null, 2));

      const response = await fetch('/api/document/save-analysis-result', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(saveData)
      });

      if (response.ok) {
        const result = await response.json();
        setError(null);
        // 목록 새로고침
        await fetchSavedResults();
        onSaveResult(result);
      } else {
        setError('결과 저장에 실패했습니다.');
      }
    } catch (err) {
      setError('저장 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 저장된 결과 불러오기
  const handleLoadResult = async (filename: string) => {
    try {
      setLoading(true);
      console.log('🔍 파일 불러오기 시작:', filename);
      
      const response = await fetch(`/api/document/load-analysis-result/${filename}`);
      console.log('📡 API 응답 상태:', response.status, response.statusText);
      
      if (response.ok) {
        const result = await response.json();
        console.log('📄 받은 응답 전체:', JSON.stringify(result, null, 2));
        
        if (result.status === 'success' && result.data) {
          console.log('✅ 성공적으로 불러온 데이터:', JSON.stringify(result.data, null, 2));
          onLoadResult(result.data);
          setError(null);
          alert('✅ 분석 결과를 성공적으로 불러왔습니다! 메인 화면에서 확인하세요.');
        } else {
          console.log('❌ API 응답 오류:', result);
          setError(result.message || '결과 불러오기에 실패했습니다.');
        }
      } else {
        const errorText = await response.text();
        console.log('❌ HTTP 오류:', response.status, errorText);
        setError(`HTTP 오류: ${response.status}`);
      }
    } catch (err) {
      console.error('❌ 불러오기 중 예외:', err);
      setError(`불러오기 중 오류: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setLoading(false);
    }
  };

  // 저장된 결과 삭제
  const handleDeleteResult = async (filename: string) => {
    if (!confirm('이 결과를 삭제하시겠습니까?')) return;

    try {
      setLoading(true);
      const response = await fetch(`/api/document/delete-analysis-result/${filename}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        await fetchSavedResults();
        setError(null);
      } else {
        setError('삭제에 실패했습니다.');
      }
    } catch (err) {
      setError('삭제 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 날짜 포맷팅
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <>
      {/* 오른쪽 사이드바 */}
      <div className={`fixed top-0 right-0 h-full bg-white shadow-xl transform transition-transform duration-300 z-50 ${
        isOpen ? 'translate-x-0' : 'translate-x-full'
      }`} style={{ width: '400px' }}>
        <div className="flex flex-col h-full">
          {/* 헤더 */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">
              💾 저장된 결과
            </h2>
            <button
              onClick={onToggle}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg"
            >
              <ChevronRightIcon className="h-5 w-5" />
            </button>
          </div>

          {/* 현재 결과 저장 섹션 */}
          <div className="p-4 border-b border-gray-200 bg-blue-50">
            <h3 className="text-sm font-medium text-blue-900 mb-2">현재 결과 저장</h3>
            <button
              onClick={handleSaveCurrentResult}
              disabled={loading || (!currentResults.documentAnalysis && !currentResults.integratedAnalysis)}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <BookmarkIcon className="h-4 w-4" />
              {loading ? '저장 중...' : '현재 결과 저장'}
            </button>
            {currentResults.documentAnalysis && (
              <p className="text-xs text-blue-600 mt-1">
                📄 문서 분석 결과 준비됨
              </p>
            )}
            {currentResults.integratedAnalysis && (
              <p className="text-xs text-blue-600 mt-1">
                🎯 통합 분석 결과 준비됨
              </p>
            )}
          </div>

          {/* 저장된 결과 목록 */}
          <div className="flex-1 overflow-y-auto p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-gray-900">저장된 결과 목록</h3>
              <button
                onClick={fetchSavedResults}
                disabled={loading}
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                🔄 새로고침
              </button>
            </div>

            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-700 font-medium">오류 발생:</p>
                <p className="text-xs text-red-600 mt-1 whitespace-pre-wrap">{error}</p>
                <div className="mt-2 text-xs text-gray-500">
                  💡 <strong>해결 방법:</strong> F12 키 누르고 Console 탭에서 자세한 로그를 확인하세요.
                </div>
              </div>
            )}

            {loading && (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            )}

            <div className="space-y-3">
              {savedResults.map((result, index) => (
                <div key={index} className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <DocumentTextIcon className="h-4 w-4 text-gray-500" />
                        <span className="text-sm font-medium text-gray-900">
                          {result.metadata.analysis_type === 'integrated' ? '🎯 통합 분석' : '📄 문서 분석'}
                        </span>
                      </div>
                      <div className="text-xs text-gray-600 mb-2">
                        <div className="flex items-center gap-1">
                          <ClockIcon className="h-3 w-3" />
                          {formatDate(result.metadata.saved_at || result.metadata.timestamp || new Date().toISOString())}
                        </div>
                        <div className="mt-1">
                          📝 {result.metadata.resume_file || '이력서 없음'}
                        </div>
                        <div>
                          📋 {result.metadata.job_file || '채용공고 없음'}
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleLoadResult(result.filename)}
                          className="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700"
                        >
                          불러오기
                        </button>
                        <button
                          onClick={() => handleDeleteResult(result.filename)}
                          className="px-3 py-1 bg-red-600 text-white text-xs rounded hover:bg-red-700"
                        >
                          <TrashIcon className="h-3 w-3" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}

              {!loading && savedResults.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <DocumentTextIcon className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                  <p className="text-sm">저장된 결과가 없습니다.</p>
                  <p className="text-xs mt-1">분석 결과를 저장해보세요!</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* 토글 버튼 (오른쪽 가장자리) */}
      {!isOpen && (
        <button
          onClick={onToggle}
          className="fixed top-1/2 right-0 transform -translate-y-1/2 bg-blue-600 text-white p-3 rounded-l-lg shadow-lg hover:bg-blue-700 z-40"
        >
          <ChevronLeftIcon className="h-5 w-5" />
        </button>
      )}

      {/* 오버레이 */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-25 z-40"
          onClick={onToggle}
        />
      )}
    </>
  );
};

export default ResultSidebar; 