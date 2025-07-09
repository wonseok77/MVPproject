#!/bin/bash

echo "=== KT DS Interview Analysis System - Azure Startup ==="
echo "Working directory: $(pwd)"
echo "Directory contents:"
ls -la

# Python 의존성 설치
echo "Installing Python dependencies..."
pip install -r requirements.txt

# 프론트엔드 빌드 확인
echo "Checking for frontend build..."
if [ -d "UI/dist" ]; then
    echo "✅ Frontend build found!"
    echo "Frontend files:"
    ls -la UI/dist/
else
    echo "❌ Frontend build not found!"
    echo "Checking UI directory:"
    if [ -d "UI" ]; then
        echo "UI directory exists, attempting to build..."
        cd UI
        npm install
        npm run build
        cd ..
    else
        echo "❌ UI directory not found!"
    fi
fi

# Python 경로 설정 및 백엔드 서버 시작
echo ""
echo "🚀 Starting backend server..."
echo "Port: ${PORT:-8000}"
echo "Setting up Python path..."

# 현재 디렉토리를 PYTHONPATH에 추가
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
echo "PYTHONPATH: $PYTHONPATH"

# 백엔드 디렉토리 확인
echo "Backend directory contents:"
ls -la backend/
ls -la backend/app/

# 서버 실행 (절대 경로 사용)
cd /home/site/wwwroot
exec python -m uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000} 