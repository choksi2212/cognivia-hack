@echo off
echo ============================================
echo  SITARA - Starting Backend API Server
echo ============================================
echo.
cd backend
echo Current directory: %CD%
echo.
echo Starting FastAPI server...
echo The API will be available at: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
python main.py
