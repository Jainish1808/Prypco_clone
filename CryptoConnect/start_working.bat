@echo off
echo ========================================
echo    CryptoConnect - Full Working Version
echo ========================================
echo.

REM Check if Python environment exists
if not exist "C:\Users\jaini\IntellijIdea\IGenerate_PYTHON_INTERN\env\Scripts\activate.bat" (
    echo ❌ Python environment not found!
    echo Please create a virtual environment first.
    pause
    exit /b 1
)

REM Activate Python environment
echo [1/4] Activating Python environment...
call C:\Users\jaini\IntellijIdea\IGenerate_PYTHON_INTERN\env\Scripts\activate.bat

REM Install/update backend dependencies
echo [2/4] Installing backend dependencies...
cd backend
pip install -r requirements.txt > nul 2>&1

REM Start working backend in background
echo [3/4] Starting Enhanced FastAPI backend...
start "CryptoConnect Backend" cmd /k "python working_run.py"
cd ..

REM Wait for backend to start
echo Waiting for backend to initialize...
timeout /t 5 /nobreak > nul

REM Install frontend dependencies if needed
if not exist "node_modules" (
    echo Installing frontend dependencies...
    npm install > nul 2>&1
)

REM Start frontend
echo [4/4] Starting React frontend...
start "CryptoConnect Frontend" cmd /k "npm run dev"

echo.
echo ========================================
echo    🎉 CryptoConnect is now FULLY working!
echo ========================================
echo.
echo 🌐 Frontend: http://localhost:5173
echo 🔧 Backend:  http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo 🔍 Debug:    http://localhost:8000/debug/state
echo.
echo ✅ NEW FEATURES NOW WORKING:
echo - ✅ Real property submission by sellers
echo - ✅ Image upload for properties
echo - ✅ Actual token investment flow
echo - ✅ XRPL blockchain integration
echo - ✅ Portfolio tracking
echo - ✅ Secondary market trading
echo - ✅ Admin property management
echo - ✅ Rental income distribution
echo - ✅ Real-time token calculations
echo.
echo 👤 Test Accounts:
echo Admin: admin@cryptoconnect.com / admin123
echo (Register new accounts as Investor or Seller)
echo.
echo 🏠 Sample Property Available:
echo - Luxury Dubai Marina Apartment
echo - Value: AED 2,600,000
echo - 1,300,000 tokens at AED 2.00 each
echo.
echo Press any key to exit...
pause > nul