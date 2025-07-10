#!/bin/bash
set -e

echo "=== KT DS 면접 분석 시스템 배포 스크립트 ==="
echo "Current directory: $(pwd)"
echo "Contents: $(ls -la)"

# 1. Python 의존성 설치
echo "Installing Python dependencies..."
pip install -r requirements.txt

# 2. 프론트엔드 빌드 확인
if [ -d "UI/dist" ]; then
    echo "Frontend build found!"
    echo "Frontend files:"
    ls -la UI/dist/
else
    echo "Frontend build not found. Building now..."
    
    # UI 디렉토리 존재 확인
    if [ ! -d "UI" ]; then
        echo "ERROR: UI directory not found!"
        ls -la
        exit 1
    fi
    
    cd UI
    echo "Frontend directory contents: $(ls -la)"
    
    # Node.js 의존성 설치 및 빌드
    npm install
    npm run build
    
    cd ..
fi

# 3. 서버 실행
echo ""
echo "Starting backend server..."
echo "Frontend build directory: UI/dist"
echo "Port: ${PORT:-8000}"
echo "Backend will serve frontend at root path (/)"
echo "API endpoints available at /api/*"
echo ""

python -m uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}

# Fixed for Linux deployment - LF line endings 