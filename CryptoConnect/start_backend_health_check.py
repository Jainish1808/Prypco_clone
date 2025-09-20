#!/usr/bin/env python3
"""
Quick backend startup and health check script for CryptoConnect
"""

import sys
import os
import asyncio
import requests
import time

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        import xrpl
        print("✅ xrpl-py is installed")
    except ImportError:
        print("❌ xrpl-py not found. Please install: pip install xrpl-py")
        return False
    
    try:
        import httpx
        print("✅ httpx is installed")
    except ImportError:
        print("❌ httpx not found. Please install: pip install httpx")
        return False
    
    try:
        import fastapi
        print("✅ fastapi is installed")
    except ImportError:
        print("❌ fastapi not found. Please install: pip install fastapi")
        return False
        
    try:
        import uvicorn
        print("✅ uvicorn is installed")
    except ImportError:
        print("❌ uvicorn not found. Please install: pip install uvicorn")
        return False
        
    return True

def check_env_file():
    """Check if .env file exists and has required variables"""
    print("\n🔧 Checking environment configuration...")
    
    env_path = os.path.join("backend", ".env")
    if not os.path.exists(env_path):
        print("❌ .env file not found in backend directory")
        return False
    
    print("✅ .env file exists")
    
    # Read and check required variables
    with open(env_path, 'r') as f:
        content = f.read()
    
    required_vars = ["ISSUER_WALLET_SEED", "MONGODB_URL", "JWT_SECRET_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if f"{var}=" not in content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All required environment variables are set")
    return True

def start_backend():
    """Start the FastAPI backend"""
    print("\n🚀 Starting backend server...")
    
    os.chdir("backend")
    
    # Start the backend server
    import subprocess
    try:
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "app.main:app",
            "--reload", "--host", "0.0.0.0", "--port", "8000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("✅ Backend server started")
        print("🌐 Server running at: http://localhost:8000")
        print("📚 API docs at: http://localhost:8000/docs")
        
        return process
    except Exception as e:
        print(f"❌ Failed to start backend: {str(e)}")
        return None

def check_backend_health():
    """Check if backend is healthy"""
    print("\n🏥 Checking backend health...")
    
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("✅ Backend is healthy and responding")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"⏳ Waiting for backend to start... ({attempt + 1}/{max_attempts})")
        time.sleep(1)
    
    print("❌ Backend health check failed")
    return False

def main():
    """Main startup function"""
    print("🚀 CryptoConnect Backend Startup Check")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n💥 Dependency check failed. Please install missing packages.")
        return False
    
    # Check environment
    if not check_env_file():
        print("\n💥 Environment check failed. Please fix configuration.")
        return False
    
    print("\n✅ All checks passed! Backend should be ready to start.")
    
    # Ask user if they want to start the backend
    print("\nWould you like to start the backend now? (y/n): ", end="")
    choice = input().lower().strip()
    
    if choice in ['y', 'yes']:
        process = start_backend()
        if process:
            print("\n🎉 Backend startup completed!")
            print("\nPress Ctrl+C to stop the server...")
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n👋 Stopping server...")
                process.terminate()
    else:
        print("\n👍 Ready to start! Run this when ready:")
        print("cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")

if __name__ == "__main__":
    main()