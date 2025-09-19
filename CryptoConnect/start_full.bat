@echo off
echo ========================================
echo    CryptoConnect Full System Startup
echo ========================================
echo.

REM Activate Python environment
echo [1/3] Activating Python environment...
call C:\Users\jaini\IntellijIdea\IGenerate_PYTHON_INTERN\env\Scripts\activate.bat

REM Start full backend in background
echo [2/3] Starting Full FastAPI backend with Database...
cd backend
start "CryptoConnect Backend" cmd /k "python full_run.py"
cd ..

REM Wait a moment for backend to start
timeout /t 5 /nobreak > nul

REM Start frontend
echo [3/3] Starting React frontend...
start "CryptoConnect Frontend" cmd /k "npm run dev"

echo.
echo ========================================
echo    CryptoConnect Full System Running!
echo ========================================
echo.
echo Frontend: http://localhost:5173
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Features:
echo - Full MongoDB integration
echo - User registration and authentication
echo - Property management
echo - JWT token security
echo - Sample data included
echo.
echo Admin Login: admin@cryptoconnect.com / admin123
echo.
echo Press any key to exit...
pause > nul