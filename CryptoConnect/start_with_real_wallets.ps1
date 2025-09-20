# CryptoConnect with Real XRP Wallets Startup Script
# This script starts the platform with your 4 real XRP testnet wallets

Write-Host "🚀 Starting CryptoConnect with Real XRP Wallets" -ForegroundColor Green
Write-Host "=" * 60

# Display your XRP wallet addresses
Write-Host "`n💰 Your XRP Testnet Wallets:" -ForegroundColor Cyan
Write-Host "1. Address: rGghB5Kp9YEQhZbxg7Pxm3FGd6gZsytQS8" -ForegroundColor Yellow
Write-Host "   Secret:  sEd7t6iGCmeYpBMW4yQxzK8FnJNpsrh" -ForegroundColor Gray
Write-Host "   Explorer: https://testnet.xrpl.org/accounts/rGghB5Kp9YEQhZbxg7Pxm3FGd6gZsytQS8"

Write-Host "`n2. Address: rnDmRyddBqCDkKBWSnKkzy5ZqtRoVjyDFg" -ForegroundColor Yellow
Write-Host "   Secret:  sEdSq6vVpKeoxDWARwpxs2KuEe1XPWU" -ForegroundColor Gray
Write-Host "   Explorer: https://testnet.xrpl.org/accounts/rnDmRyddBqCDkKBWSnKkzy5ZqtRoVjyDFg"

Write-Host "`n3. Address: rLB8NiA8MdTS68BXzfu3wwgsZp5uEnyU85" -ForegroundColor Yellow
Write-Host "   Secret:  sEd76oZCyQ4bwMV2SbLNUhULyHLBY29" -ForegroundColor Gray
Write-Host "   Explorer: https://testnet.xrpl.org/accounts/rLB8NiA8MdTS68BXzfu3wwgsZp5uEnyU85"

Write-Host "`n4. Address: rJ86bTZkm59iAwV68ZJTq9GdSjBwM5DAw1" -ForegroundColor Yellow
Write-Host "   Secret:  sEdVgnP4k7xVASCmBhkTdgcrH4nYjHw" -ForegroundColor Gray
Write-Host "   Explorer: https://testnet.xrpl.org/accounts/rJ86bTZkm59iAwV68ZJTq9GdSjBwM5DAw1"

Write-Host "`n🔧 Installing dependencies..." -ForegroundColor Cyan
npm install
pip install xrpl-py httpx

Write-Host "`n🗄️ Starting MongoDB..." -ForegroundColor Cyan
Start-Process "mongod" -WindowStyle Hidden

Write-Host "`n🔙 Starting Backend Server..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-Command", "cd backend; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" -WindowStyle Normal

Write-Host "`n⏳ Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "`n🎨 Starting Frontend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-Command", "cd client; npm run dev" -WindowStyle Normal

Write-Host "`n⏳ Waiting for frontend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host "`n✅ CryptoConnect is starting up!" -ForegroundColor Green
Write-Host "🌐 Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "🔧 Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan

Write-Host "`n🧪 Test the complete flow:" -ForegroundColor Magenta
Write-Host "python test_complete_xrp_flow.py" -ForegroundColor White

Write-Host "`n📋 How to use:" -ForegroundColor Cyan
Write-Host "1. Register as a user (investor or seller)" -ForegroundColor White
Write-Host "2. Connect one of your XRP wallets above" -ForegroundColor White
Write-Host "3. Submit a property (if seller) - creates real XRP tokens!" -ForegroundColor White
Write-Host "4. Buy property tokens (if investor)" -ForegroundColor White
Write-Host "5. View your tokens on XRP testnet explorer" -ForegroundColor White
Write-Host "6. Transfer tokens to other users" -ForegroundColor White

Write-Host "`n🎉 All your property tokens will be REAL and visible on:" -ForegroundColor Green
Write-Host "https://testnet.xrpl.org" -ForegroundColor Yellow

Write-Host "`nPress any key to open the application..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Open the application
Start-Process "http://localhost:5173"