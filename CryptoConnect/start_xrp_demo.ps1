#!/usr/bin/env pwsh
# Enhanced XRP Tokenization Demo Launcher

Write-Host "🚀 Starting Enhanced XRP Tokenization System" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

# Start backend
Write-Host "📡 Starting FastAPI backend with XRP integration..." -ForegroundColor Yellow
Start-Process PowerShell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Display information
Write-Host ""
Write-Host "✅ Backend started with XRP Ledger integration!" -ForegroundColor Green
Write-Host ""
Write-Host "🔗 API Endpoints:" -ForegroundColor Cyan
Write-Host "   - Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   - API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "🪙 XRP Token Features:" -ForegroundColor Cyan
Write-Host "   - Real tokens created on XRP testnet" -ForegroundColor White
Write-Host "   - View tokens at: https://testnet.xrpl.org/" -ForegroundColor White
Write-Host "   - Token transfers between users" -ForegroundColor White
Write-Host "   - Live balance verification" -ForegroundColor White
Write-Host ""
Write-Host "🧪 Test Scripts Available:" -ForegroundColor Cyan
Write-Host "   - python test_xrp_tokenization.py" -ForegroundColor White
Write-Host "   - python test_token_transfers.py" -ForegroundColor White
Write-Host ""
Write-Host "📚 Read XRP_TOKENIZATION_GUIDE.md for details" -ForegroundColor Yellow
Write-Host ""
Write-Host "🎉 Ready to tokenize properties on XRP Ledger!" -ForegroundColor Green