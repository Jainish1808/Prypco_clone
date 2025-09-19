#!/usr/bin/env python3
"""
Quick Setup Verification for CryptoConnect
"""

import sys
import os

def check_files():
    """Check if all required files exist"""
    print("🔍 Checking required files...")
    
    required_files = [
        "backend/.env",
        "backend/app/main.py",
        "backend/run.py",
        "client/src/App.tsx",
        "package.json"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"   ✅ {file_path}")
    
    if missing_files:
        print(f"   ❌ Missing files: {missing_files}")
        return False
    
    return True

def check_env_config():
    """Check environment configuration"""
    print("\n🔍 Checking environment configuration...")
    
    env_path = "backend/.env"
    if not os.path.exists(env_path):
        print("   ❌ .env file not found")
        return False
    
    with open(env_path, 'r') as f:
        env_content = f.read()
    
    required_vars = [
        "MONGODB_URL",
        "JWT_SECRET_KEY", 
        "ISSUER_WALLET_SEED",
        "ISSUER_WALLET_ADDRESS"
    ]
    
    for var in required_vars:
        if var in env_content and f"{var}=" in env_content:
            # Check if it has a value
            for line in env_content.split('\n'):
                if line.startswith(f"{var}=") and len(line.split('=', 1)[1].strip()) > 0:
                    print(f"   ✅ {var} configured")
                    break
            else:
                print(f"   ⚠️  {var} found but empty")
        else:
            print(f"   ❌ {var} not found")
            return False
    
    return True

def check_python_packages():
    """Check if required Python packages are installed"""
    print("\n🔍 Checking Python packages...")
    
    required_packages = [
        "fastapi",
        "uvicorn", 
        "motor",
        "beanie",
        "xrpl"
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} not installed")
            return False
    
    return True

def main():
    """Run all verification checks"""
    print("🚀 CryptoConnect Setup Verification")
    print("=" * 40)
    
    checks = [
        ("File Structure", check_files),
        ("Environment Config", check_env_config),
        ("Python Packages", check_python_packages)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"   ❌ {check_name} check failed: {str(e)}")
            all_passed = False
    
    print("\n" + "=" * 40)
    
    if all_passed:
        print("🎉 All checks passed! Your setup is ready.")
        print("\nTo start CryptoConnect:")
        print("1. Run: start_cryptoconnect.bat (or .ps1)")
        print("2. Or manually:")
        print("   - Backend: cd backend && python run.py")
        print("   - Frontend: npm run dev")
        print("\nAccess URLs:")
        print("- Frontend: http://localhost:5173")
        print("- Backend: http://localhost:8000")
        print("- API Docs: http://localhost:8000/docs")
        print("\nAdmin Login: admin@cryptoconnect.com / admin123")
    else:
        print("❌ Some checks failed. Please review the issues above.")
        print("\nCommon solutions:")
        print("1. Ensure MongoDB is running")
        print("2. Run: pip install -r backend/requirements.txt")
        print("3. Check backend/.env file configuration")

if __name__ == "__main__":
    main()