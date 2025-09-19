@echo off
echo Starting CryptoConnect Full Development Environment...

REM Check if MongoDB is running
echo Checking MongoDB...
tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo ✓ MongoDB is running
) else (
    echo ❌ MongoDB is not running. Please start MongoDB first.
    echo You can start MongoDB with: net start MongoDB
    pause
    exit /b 1
)

REM Start backend in a new window
echo Starting Backend...
start "CryptoConnect Backend" cmd /k "cd /d %~dp0backend && python run.py"

REM Wait a bit for backend to start
timeout /t 5 /nobreak >nul

REM Start frontend in a new window
echo Starting Frontend...
start "CryptoConnect Frontend" cmd /k "cd /d %~dp0 && npm run dev"

echo.
echo ✓ Both backend and frontend are starting...
echo ✓ Backend will be available at: http://localhost:8000
echo ✓ Frontend will be available at: http://localhost:5173
echo ✓ API Documentation: http://localhost:8000/docs
echo.
echo Press any key to close this window (services will continue running)
pause >nul