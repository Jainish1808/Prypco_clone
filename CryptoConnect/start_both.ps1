# CryptoConnect Startup Script
Write-Host "🚀 Starting CryptoConnect..." -ForegroundColor Cyan

# Activate Python environment
Write-Host "Activating Python environment..." -ForegroundColor Yellow
& "C:\Users\jaini\IntellijIdea\IGenerate_PYTHON_INTERN\env\Scripts\Activate.ps1"

# Start backend in new window
Write-Host "Starting FastAPI backend..." -ForegroundColor Yellow
$backendJob = Start-Job -ScriptBlock {
    Set-Location "C:\Users\jaini\IntellijIdea\IGenerate_PYTHON_INTERN\Project_with_Blockchain\Project_1\CryptoConnect\backend"
    & "C:\Users\jaini\IntellijIdea\IGenerate_PYTHON_INTERN\env\Scripts\python.exe" "simple_run.py"
}

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start frontend in new window
Write-Host "Starting React frontend..." -ForegroundColor Yellow
$frontendJob = Start-Job -ScriptBlock {
    Set-Location "C:\Users\jaini\IntellijIdea\IGenerate_PYTHON_INTERN\Project_with_Blockchain\Project_1\CryptoConnect"
    npm run dev
}

Write-Host ""
Write-Host "✅ Both services are starting!" -ForegroundColor Green
Write-Host "Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "Backend:  http://localhost:8000" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop both services" -ForegroundColor Yellow

# Wait for user to stop
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    Write-Host "Stopping services..." -ForegroundColor Red
    Stop-Job $backendJob -Force
    Stop-Job $frontendJob -Force
    Remove-Job $backendJob -Force
    Remove-Job $frontendJob -Force
}