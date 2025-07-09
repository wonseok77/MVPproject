#!/usr/bin/env python3
"""
Azure Web App용 서버 실행 스크립트
"""
import sys
import os
from pathlib import Path

# 현재 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

print(f"Current directory: {current_dir}")
print(f"Python path: {sys.path}")

# 백엔드 모듈 확인
try:
    from backend.app.main import app
    print("✅ Backend app successfully imported!")
except ImportError as e:
    print(f"❌ Failed to import backend app: {e}")
    print("Directory contents:")
    print(list(current_dir.iterdir()))
    sys.exit(1)

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting server on port {port}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    ) 