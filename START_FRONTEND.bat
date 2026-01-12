@echo off
echo ============================================
echo  SITARA - Starting Frontend Dev Server
echo ============================================
echo.
cd frontend
echo Current directory: %CD%
echo.
echo Installing dependencies (if needed)...
call npm install
echo.
echo Starting Next.js dev server...
echo The app will be available at: http://localhost:3000
echo.
call npm run dev
