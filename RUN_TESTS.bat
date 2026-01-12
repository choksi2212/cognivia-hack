@echo off
echo ========================================
echo SITARA - Complete System Tests
echo ========================================
echo.

echo Starting backend server...
start /B python backend\main.py

echo Waiting for server to start...
timeout /t 8 /nobreak > nul

echo.
echo ========================================
echo Running Tests...
echo ========================================
echo.

echo Test 1: Health Check
curl -s http://localhost:8000/health
echo.
echo.

echo Test 2: Risk Assessment (Ahmedabad)
curl -s -X POST http://localhost:8000/api/assess-risk -H "Content-Type: application/json" -d "{\"location\":{\"latitude\":22.6823,\"longitude\":72.8703}}"
echo.
echo.

echo Test 3: Agent State
curl -s http://localhost:8000/api/agent/state
echo.
echo.

echo Test 4: Database Stats
curl -s http://localhost:8000/api/database/stats
echo.
echo.

echo ========================================
echo Tests Complete!
echo ========================================
echo.
echo Press any key to stop backend server...
pause > nul

taskkill /F /IM python.exe /FI "WINDOWTITLE eq *main.py*" 2>nul
echo.
echo Backend stopped.
pause
