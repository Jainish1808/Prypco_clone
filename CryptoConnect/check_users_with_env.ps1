# Check Database Users with Virtual Environment
# This script activates your virtual environment and checks database users

Write-Host "🔧 Activating Virtual Environment..." -ForegroundColor Cyan
& "C:\Users\jaini\IntellijIdea\IGenerate_PYTHON_INTERN\env\Scripts\Activate.ps1"

Write-Host "🔍 Checking Database Users..." -ForegroundColor Green
python check_database_users.py

Write-Host "`n💡 Next steps:" -ForegroundColor Yellow
Write-Host "1. To assign wallets to existing users: python assign_wallets_to_existing_users.py" -ForegroundColor White
Write-Host "2. For manual assignment: python manual_wallet_assignment.py" -ForegroundColor White