@echo off
echo Starting CryptoConnect FastAPI Backend...

REM Activate virtual environment
call C:\Users\jaini\IntellijIdea\IGenerate_PYTHON_INTERN\env\Scripts\activate.bat

REM Install requirements if needed
pip install -r requirements.txt

REM Start the FastAPI server
python run.py

pause