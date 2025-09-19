@echo off
echo ========================================
echo    CryptoConnect Startup Script
echo ========================================
echo.

REM Activate Python environment
echo [1/4] Activating Python environment...
call C:\Users\jaini\IntellijIdea\IGenerate_PYTHON_INTERN\env\Scripts\activate.bat

REM Start backend in background
echo [2/4] Starting FastAPI backend...
cd backend
start "CryptoConnect Backend" cmd /k "python run.py"
cd ..

REM Wait a moment for backend to start
timeout /t 3 /nobreak > nul

REM Start frontend
echo [3/4] Starting React frontend...
start "CryptoConnect Frontend" cmd /k "npm run dev"

echo [4/4] Both services are starting...
echo.
echo ========================================
echo    CryptoConnect is starting up!
echo ========================================
echo.
echo Frontend: http://localhost:5173
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Admin Login:
echo Email: admin@cryptoconnect.com
echo Password: admin123
echo.
echo Press any key to exit...
pause > nul