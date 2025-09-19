# PowerShell script to start CryptoConnect FastAPI Backend
Write-Host "Starting CryptoConnect FastAPI Backend..." -ForegroundColor Green

# Activate virtual environment
& "C:\Users\jaini\IntellijIdea\IGenerate_PYTHON_INTERN\env\Scripts\Activate.ps1"

# Install requirements if needed
pip install -r requirements.txt

# Start the FastAPI server
python run.py