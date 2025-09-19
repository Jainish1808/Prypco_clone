#!/usr/bin/env python3
"""
CryptoConnect Working FastAPI Backend Runner
This version includes all the fixes and working functionality
"""
import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from app.config import settings
from app.database import connect_to_mongo
from init_db import init_database

async def startup():
    """Initialize database and create sample data"""
    print("🚀 Starting CryptoConnect Backend...")
    print("=" * 50)
    
    try:
        # Connect to database
        await connect_to_mongo()
        print("✅ Connected to MongoDB")
        
        # Initialize database with sample data
        await init_database()
        print("✅ Database initialized")
        
    except Exception as e:
        print(f"❌ Startup failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    # Run startup tasks
    startup_success = asyncio.run(startup())
    
    if startup_success:
        print("\n🎉 Backend ready! Starting server...")
        print(f"📡 API Server: http://localhost:{settings.api_port}")
        print(f"📚 API Docs: http://localhost:{settings.api_port}/docs")
        print(f"🔍 Debug State: http://localhost:{settings.api_port}/debug/state")
        print("=" * 50)
        
        # Start the server
        uvicorn.run(
            "app.main:app",
            host=settings.api_host,
            port=settings.api_port,
            reload=settings.debug
        )
    else:
        print("❌ Failed to start backend")
        sys.exit(1)