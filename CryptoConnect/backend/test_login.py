#!/usr/bin/env python3
"""
Quick test script to verify login functionality
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import connect_to_mongo, close_mongo_connection
from app.models.user import User
from app.auth import verify_password

async def test_login():
    """Test login functionality"""
    print("🧪 Testing Login Functionality")
    print("=" * 40)
    
    try:
        # Connect to database
        await connect_to_mongo()
        print("✅ Connected to MongoDB")
        
        # Find admin user by username
        admin_by_username = await User.find_one(User.username == "admin")
        print(f"Admin by username: {admin_by_username.email if admin_by_username else 'Not found'}")
        
        # Find admin user by email
        admin_by_email = await User.find_one(User.email == "admin@cryptoconnect.com")
        print(f"Admin by email: {admin_by_email.username if admin_by_email else 'Not found'}")
        
        if admin_by_username:
            # Test password verification
            password_correct = verify_password("admin123", admin_by_username.hashed_password)
            print(f"Password verification: {'✅ Correct' if password_correct else '❌ Wrong'}")
            
            print(f"\n📋 Admin User Details:")
            print(f"   ID: {admin_by_username.id}")
            print(f"   Email: {admin_by_username.email}")
            print(f"   Username: {admin_by_username.username}")
            print(f"   Role: {admin_by_username.role}")
            print(f"   Active: {admin_by_username.is_active}")
        
        print(f"\n✅ Login should work with:")
        print(f"   Username: 'admin' + Password: 'admin123'")
        print(f"   Email: 'admin@cryptoconnect.com' + Password: 'admin123'")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(test_login())