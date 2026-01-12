@echo off
echo ========================================
echo SITARA Database Setup
echo ========================================
echo.

:: Create .env file for frontend
echo Creating frontend .env file...
(
echo # PostgreSQL Database Connection
echo DATABASE_URL="postgresql://postgres:niklaus2212@localhost:5432/sitara?schema=public"
echo.
echo # Next.js
echo NEXT_PUBLIC_API_URL=http://localhost:8000
) > frontend\.env

:: Create .env file for backend
echo Creating backend .env file...
(
echo # PostgreSQL Database Connection
echo DATABASE_URL="postgresql://postgres:niklaus2212@localhost:5432/sitara?schema=public"
echo.
echo # Model paths
echo MODEL_PATH=models/risk_model.joblib
echo SCALER_PATH=models/feature_scaler.joblib
echo FEATURE_NAMES_PATH=models/feature_names.json
) > backend\.env

echo.
echo .env files created!
echo.

:: Create database
echo Creating PostgreSQL database 'sitara'...
psql -U postgres -c "CREATE DATABASE sitara;" 2>nul
if %errorlevel% equ 0 (
    echo Database created successfully!
) else (
    echo Database might already exist, continuing...
)

echo.
:: Run Prisma migrations
echo Running Prisma migrations to create tables...
cd frontend
call npx prisma migrate dev --name init

echo.
echo ========================================
echo Database setup complete!
echo ========================================
echo.
echo You can now:
echo 1. Run the backend: START_BACKEND.bat
echo 2. Run the frontend: START_FRONTEND.bat
echo.
pause
