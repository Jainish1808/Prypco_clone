# CryptoConnect Working Version PowerShell Startup Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    CryptoConnect Working Version" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Activate Python environment
Write-Host "[1/3] Activating Python environment..." -ForegroundColor Yellow
& "C:\Users\jaini\IntellijIdea\IGenerate_PYTHON_INTERN\env\Scripts\Activate.ps1"

# Start working backend in background
Write-Host "[2/3] Starting Working FastAPI backend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python working_run.py" -WindowStyle Normal

# Wait for backend to start
Start-Sleep -Seconds 3

# Start frontend
Write-Host "[3/3] Starting React frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev" -WindowStyle Normal

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "    CryptoConnect is now running!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "Debug:    http://localhost:8000/debug/state" -ForegroundColor White
Write-Host ""
Write-Host "Features Working:" -ForegroundColor Cyan
Write-Host "- User registration and login" -ForegroundColor White
Write-Host "- Authentication with tokens" -ForegroundColor White
Write-Host "- Property listings" -ForegroundColor White
Write-Host "- KYC submission" -ForegroundColor White
Write-Host "- No more 500 errors!" -ForegroundColor Green
Write-Host ""
Write-Host "Test Accounts:" -ForegroundColor Cyan
Write-Host "Admin: admin@cryptoconnect.com / admin123" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")