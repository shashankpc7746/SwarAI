@echo off
echo ========================================
echo   SwarAI - Quick Start
echo ========================================
echo.

echo [1/4] Installing Backend Dependencies...
cd backend
pip install PyJWT python-jose[cryptography] passlib[bcrypt]
if errorlevel 1 (
    echo ERROR: Failed to install backend dependencies
    pause
    exit /b 1
)

echo.
echo [2/4] Starting Backend Server...
start "SwarAI Backend" cmd /k "python main.py"
timeout /t 3 /nobreak >nul

echo.
echo [3/4] Installing Frontend Dependencies...
cd ..\frontend
if not exist "node_modules" (
    echo Installing Node.js packages...
    call npm install
    if errorlevel 1 (
        echo ERROR: Failed to install frontend dependencies
        pause
        exit /b 1
    )
)

echo.
echo [4/4] Starting Frontend Server...
start "SwarAI Frontend" cmd /k "npm run dev"

echo.
echo ========================================
echo   SwarAI is starting!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Login page will open automatically in 10 seconds...
echo.
timeout /t 10 /nobreak >nul

start http://localhost:3000

echo.
echo Press any key to close this window...
pause >nul
