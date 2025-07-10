#!/bin/bash

echo "=== KT DS Interview Analysis System - Azure Startup v2.0 ==="
echo "Startup script updated: $(date)"
echo "Working directory: $(pwd)"
echo "Directory contents:"
ls -la

# Python 의존성 설치
echo "Installing Python dependencies..."
pip install -r requirements.txt

# 프론트엔드 빌드 확인
echo "Checking for frontend build..."
if [ -d "UI/dist" ]; then
    echo "Frontend build found!"
    echo "Frontend files:"
    ls -la UI/dist/
else
    echo "Frontend build not found!"
    echo "Checking UI directory:"
    if [ -d "UI" ]; then
        echo "UI directory exists, attempting to build..."
        cd UI
        npm install
        npm run build
        cd ..
    else
        echo "UI directory not found!"
    fi
fi

# Python 경로 설정 및 백엔드 서버 시작
echo ""
echo "Starting backend server..."
echo "Port: ${PORT:-8000}"
echo "Setting up Python path..."

# 현재 디렉토리를 PYTHONPATH에 추가
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
echo "PYTHONPATH: $PYTHONPATH"

# 백엔드 디렉토리 확인
echo "=== DETAILED BACKEND DEBUGGING ==="
echo "Backend directory contents:"
ls -la backend/
echo "Backend/app directory contents:"
ls -la backend/app/
echo "Looking for Python files in backend:"
find backend -name "*.py" -type f
echo "=== END DEBUGGING ==="

# 서버 실행 방법 변경 - backend 디렉토리로 이동
echo "Attempting to start server from backend directory..."
cd /home/site/wwwroot/backend
echo "Current directory after cd: $(pwd)"
echo "Python files in current directory:"
find . -name "*.py" | head -10

# 서버 실행
echo "Starting uvicorn server..."
exec python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}

# Fixed for Linux deployment - LF line endings - Updated v2.0 