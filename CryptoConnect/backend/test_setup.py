#!/usr/bin/env python3
"""
Setup Test Script for CryptoConnect
This script tests all major components to ensure everything is working correctly.
"""

import asyncio
import aiohttp
import json
from app.database import connect_to_mongo, close_mongo_connection
from app.models.user import User
from app.models.property import Property
from app.services.xrpl_service import xrpl_service

async def test_database_connection():
    """Test MongoDB connection"""
    print("🔍 Testing Database Connection...")
    try:
        await connect_to_mongo()
        print("✅ Database connection successful")
        
        # Test user count
        user_count = await User.find().count()
        property_count = await Property.find().count()
        
        print(f"   Users in database: {user_count}")
        print(f"   Properties in database: {property_count}")
        
        await close_mongo_connection()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

async def test_xrpl_connection():
    """Test XRPL connection"""
    print("\n🔍 Testing XRPL Connection...")
    try:
        if not xrpl_service.issuer_wallet:
            print("⚠️  XRPL issuer wallet not configured")
            print("   Run 'python setup_xrpl_wallet.py' to set up wallet")
            return False
        
        # Test account info
        account_info = await xrpl_service.get_account_info(xrpl_service.issuer_wallet.address)
        if account_info:
            print("✅ XRPL connection successful")
            print(f"   Issuer address: {xrpl_service.issuer_wallet.address}")
            print(f"   Account balance: {account_info.get('Balance', 'Unknown')} drops")
            return True
        else:
            print("❌ Failed to get XRPL account info")
            return False
    except Exception as e:
        print(f"❌ XRPL connection failed: {str(e)}")
        return False

async def test_api_endpoints():
    """Test API endpoints"""
    print("\n🔍 Testing API Endpoints...")
    
    base_url = "http://localhost:8000"
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test health endpoint
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    print("✅ Health endpoint working")
                else:
                    print(f"❌ Health endpoint failed: {response.status}")
                    return False
            
            # Test root endpoint
            async with session.get(f"{base_url}/") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Root endpoint working: {data.get('message', 'No message')}")
                else:
                    print(f"❌ Root endpoint failed: {response.status}")
                    return False
            
            # Test properties endpoint (should work without auth for listing)
            async with session.get(f"{base_url}/properties") as response:
                if response.status in [200, 401]:  # 401 is expected without auth
                    print("✅ Properties endpoint accessible")
                else:
                    print(f"❌ Properties endpoint failed: {response.status}")
                    return False
        
        return True
    except Exception as e:
        print(f"❌ API endpoint test failed: {str(e)}")
        print("   Make sure the backend server is running on port 8000")
        return False

async def test_user_registration():
    """Test user registration flow"""
    print("\n🔍 Testing User Registration...")
    
    base_url = "http://localhost:8000"
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test user registration
            test_user = {
                "email": "test@example.com",
                "username": "testuser",
                "password": "testpass123",
                "role": "investor",
                "first_name": "Test",
                "last_name": "User"
            }
            
            async with session.post(
                f"{base_url}/auth/register",
                json=test_user,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ User registration working")
                    print(f"   Created user: {data.get('email', 'Unknown')}")
                    return True
                elif response.status == 400:
                    error_data = await response.json()
                    if "already registered" in error_data.get("detail", ""):
                        print("✅ User registration working (user already exists)")
                        return True
                    else:
                        print(f"❌ User registration failed: {error_data.get('detail', 'Unknown error')}")
                        return False
                else:
                    print(f"❌ User registration failed: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ User registration test failed: {str(e)}")
        return False

async def run_all_tests():
    """Run all tests"""
    print("🚀 CryptoConnect Setup Test Suite")
    print("=" * 40)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("XRPL Connection", test_xrpl_connection),
        ("API Endpoints", test_api_endpoints),
        ("User Registration", test_user_registration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 25)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your CryptoConnect setup is working correctly.")
        print("\nYou can now:")
        print("1. Access the frontend at http://localhost:5173")
        print("2. Access the API at http://localhost:8000")
        print("3. View API docs at http://localhost:8000/docs")
        print("4. Login as admin: admin@cryptoconnect.com / admin123")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the setup.")
        print("\nCommon solutions:")
        print("1. Ensure MongoDB is running")
        print("2. Run 'python setup_xrpl_wallet.py' to configure XRPL")
        print("3. Check your .env file configuration")
        print("4. Make sure the backend server is running")

if __name__ == "__main__":
    asyncio.run(run_all_tests())