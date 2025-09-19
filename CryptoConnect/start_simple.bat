@echo off
echo ========================================
echo    CryptoConnect Simple Startup
echo ========================================
echo.

REM Activate Python environment
echo [1/3] Activating Python environment...
call C:\Users\jaini\IntellijIdea\IGenerate_PYTHON_INTERN\env\Scripts\activate.bat

REM Start simple backend in background
echo [2/3] Starting Simple FastAPI backend...
cd backend
start "CryptoConnect Backend" cmd /k "python simple_run.py"
cd ..

REM Wait a moment for backend to start
timeout /t 3 /nobreak > nul

REM Start frontend
echo [3/3] Starting React frontend...
start "CryptoConnect Frontend" cmd /k "npm run dev"

echo.
echo ========================================
echo    CryptoConnect is starting up!
echo ========================================
echo.
echo Frontend: http://localhost:5173
echo Backend:  http://localhost:8000
echo.
echo Note: This is a simplified version for testing.
echo The backend has basic endpoints but no database.
echo.
echo Press any key to exit...
pause > nul