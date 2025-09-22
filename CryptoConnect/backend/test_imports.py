#!/usr/bin/env python3
"""
Test script to check for import errors in the FastAPI app
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

print("🔍 Testing imports...")

try:
    print("1. Testing basic imports...")
    from fastapi import FastAPI
    print("✅ FastAPI imported")
    
    print("2. Testing app imports...")
    from app.main import app
    print("✅ App imported successfully")
    
    print("3. Checking routes...")
    for route in app.routes:
        print(f"   Route: {route.path} [{route.methods if hasattr(route, 'methods') else 'N/A'}]")
    
    print("🎉 All imports successful! The server should work.")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()