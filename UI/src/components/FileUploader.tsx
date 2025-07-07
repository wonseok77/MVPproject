import React, { useState, useRef } from 'react';
import { Upload, File, X, CheckCircle } from 'lucide-react';

interface FileUploaderProps {
  title: string;
  allowedTypes: string[];
  fileTypeLabel: string;
  onFileUpload: (file: File) => void;
  uploadedFile?: File;
  onRemoveFile?: () => void;
}

const FileUploader: React.FC<FileUploaderProps> = ({
  title,
  allowedTypes,
  fileTypeLabel,
  onFileUpload,
  uploadedFile,
  onRemoveFile
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleFileSelect = (file: File) => {
    const fileExtension = file.name.split('.').pop()?.toLowerCase();
    if (fileExtension && allowedTypes.includes(fileExtension)) {
      onFileUpload(file);
    } else {
      alert(`허용되지 않는 파일 형식입니다. ${fileTypeLabel} 파일만 업로드 가능합니다.`);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="mb-6">
      <h3 className="text-sm font-semibold text-gray-700 mb-2">{title}</h3>
      
      {uploadedFile ? (
        <div className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center space-x-2">
            <CheckCircle className="w-4 h-4 text-green-600" />
            <File className="w-4 h-4 text-green-600" />
            <span className="text-sm text-green-700 truncate" title={uploadedFile.name}>
              {uploadedFile.name}
            </span>
          </div>
          {onRemoveFile && (
            <button
              onClick={onRemoveFile}
              className="text-red-500 hover:text-red-700 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      ) : (
        <div
          className={`border-2 border-dashed rounded-lg p-4 transition-all cursor-pointer
            ${isDragging 
              ? 'border-blue-500 bg-blue-50' 
              : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
            }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={handleClick}
        >
          <div className="flex flex-col items-center space-y-2">
            <Upload className="w-6 h-6 text-gray-400" />
            <p className="text-xs text-gray-500 text-center">
              파일을 드래그하거나 클릭하여 업로드
            </p>
            <p className="text-xs text-gray-400">
              {fileTypeLabel}
            </p>
          </div>
        </div>
      )}
      
      <input
        ref={fileInputRef}
        type="file"
        accept={allowedTypes.map(type => `.${type}`).join(',')}
        onChange={handleFileInputChange}
        className="hidden"
      />
    </div>
  );
};

export default FileUploader;