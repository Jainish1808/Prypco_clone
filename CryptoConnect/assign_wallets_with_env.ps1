# Assign XRP Wallets with Virtual Environment
# This script activates your virtual environment and assigns wallets to users

Write-Host "🔧 Activating Virtual Environment..." -ForegroundColor Cyan
& "C:\Users\jaini\IntellijIdea\IGenerate_PYTHON_INTERN\env\Scripts\Activate.ps1"

Write-Host "🔗 Starting Wallet Assignment Tool..." -ForegroundColor Green
python manual_wallet_assignment.py