# CryptoConnect PowerShell Startup Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    CryptoConnect Startup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Activate Python environment
Write-Host "[1/4] Activating Python environment..." -ForegroundColor Yellow
& "C:\Users\jaini\IntellijIdea\IGenerate_PYTHON_INTERN\env\Scripts\Activate.ps1"

# Start backend in background
Write-Host "[2/4] Starting FastAPI backend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python run.py" -WindowStyle Normal

# Wait for backend to start
Start-Sleep -Seconds 3

# Start frontend
Write-Host "[3/4] Starting React frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev" -WindowStyle Normal

Write-Host "[4/4] Both services are starting..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "    CryptoConnect is starting up!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Admin Login:" -ForegroundColor Cyan
Write-Host "Email: admin@cryptoconnect.com" -ForegroundColor White
Write-Host "Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")