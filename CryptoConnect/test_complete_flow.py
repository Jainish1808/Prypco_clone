#!/usr/bin/env python3
"""
Complete Flow Test Script for CryptoConnect
Tests the entire XRP wallet integration and tokenization flow
"""
import requests
import json
import time

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"

# Global variable to store access token
access_token = None

def test_backend_health():
    """Test if backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        print(f"✅ Backend Health: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Backend Health: {e}")
        return False

def test_wallet_service():
    """Test wallet service endpoints"""
    try:
        # Test wallet assignment endpoint
        response = requests.post(f"{BACKEND_URL}/api/wallet/assign-to-existing-users")
        print(f"✅ Wallet Assignment: {response.status_code}")
        
        if response.status_code == 200:
            wallet_data = response.json()
            print(f"   Wallets Assigned: {wallet_data.get('wallets_assigned', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"❌ Wallet Service: {e}")
        return False

def test_user_endpoints():
    """Test user registration and authentication"""
    try:
        # Test user registration with unique email
        import time
        timestamp = int(time.time())
        test_user = {
            "email": f"test{timestamp}@example.com",
            "username": f"testuser{timestamp}",
            "password": "testpass123",
            "firstName": "Test",
            "lastName": "User",
            "userType": "seller"  # Changed to seller for property submission
        }
        
        response = requests.post(f"{BACKEND_URL}/api/register", json=test_user)
        print(f"✅ User Registration: {response.status_code}")
        if response.status_code != 200:
            print(f"   Registration Error: {response.text}")
        
        # Test user login
        login_data = {
            "username": test_user["username"],
            "password": test_user["password"]
        }
        
        login_response = requests.post(f"{BACKEND_URL}/api/login", json=login_data)
        print(f"✅ User Login: {login_response.status_code}")
        if login_response.status_code != 200:
            print(f"   Login Error: {login_response.text}")
        else:
            # Store the access token for authenticated requests
            login_result = login_response.json()
            global access_token
            access_token = login_result.get("access_token")
            print(f"   Access Token: {access_token[:20]}..." if access_token else "   No token received")
        
        return True
    except Exception as e:
        print(f"❌ User Endpoints: {e}")
        return False

def test_property_endpoints():
    """Test property submission and tokenization"""
    try:
        # Test property submission with authentication
        property_data = {
            "title": "Test Property",
            "description": "Test property for tokenization",
            "address": "123 Test Street",
            "city": "Test City",
            "country": "UAE",
            "property_type": "residential",
            "total_value": 1000000,
            "size_sqm": 150,
            "bedrooms": 3,
            "bathrooms": 2,
            "monthly_rent": 8000
        }
        
        # Use authentication header if we have a token
        headers = {}
        if 'access_token' in globals() and access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        
        response = requests.post(f"{BACKEND_URL}/api/seller/property/submit", 
                               json=property_data, headers=headers)
        print(f"✅ Property Submission: {response.status_code}")
        if response.status_code != 200:
            print(f"   Submission Error: {response.text}")
        else:
            result = response.json()
            print(f"   Property Created: {result.get('title', 'N/A')}")
            print(f"   Property ID: {result.get('id', 'N/A')}")
        
        # Test property listing
        list_response = requests.get(f"{BACKEND_URL}/api/properties")
        print(f"✅ Property Listing: {list_response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ Property Endpoints: {e}")
        return False

def main():
    """Run complete flow test"""
    print("🚀 Starting CryptoConnect Complete Flow Test")
    print("=" * 50)
    
    # Test backend health
    if not test_backend_health():
        print("❌ Backend is not running. Please start the backend first.")
        return
    
    print("\n📋 Testing Core Services:")
    print("-" * 30)
    
    # Test wallet service
    test_wallet_service()
    
    # Test user endpoints
    test_user_endpoints()
    
    # Test property endpoints
    test_property_endpoints()
    
    print("\n🎯 Manual Testing Steps:")
    print("-" * 30)
    print(f"1. Open Frontend: {FRONTEND_URL}")
    print("2. Register a new user account")
    print("3. Check dashboard for wallet assignment")
    print("4. Submit a property for tokenization")
    print("5. Test investment flow")
    print("\n✅ Test script completed!")

if __name__ == "__main__":
    main()