#!/usr/bin/env python3
"""
Test JWT authentication flow
"""
import requests
import json

def test_jwt_auth():
    """Test the complete JWT authentication flow"""
    print("🧪 Testing JWT Authentication Flow")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Step 1: Login and get token
    print("\n1️⃣ Logging in...")
    try:
        login_response = requests.post(
            f"{base_url}/api/login",
            headers={"Content-Type": "application/json"},
            json={"username": "admin", "password": "admin123"}
        )
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            token = login_data['access_token']
            user = login_data['user']
            print(f"✅ Login successful!")
            print(f"   User: {user['email']}")
            print(f"   Role: {user['role']}")
            print(f"   Token: {token[:50]}...")
        else:
            print(f"❌ Login failed: {login_response.text}")
            return
    except Exception as e:
        print(f"❌ Login request failed: {str(e)}")
        return
    
    # Step 2: Test protected endpoint with token
    print("\n2️⃣ Testing protected endpoint...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        user_response = requests.get(
            f"{base_url}/api/user",
            headers=headers
        )
        
        if user_response.status_code == 200:
            user_data = user_response.json()
            print(f"✅ User endpoint works!")
            print(f"   User: {user_data['email']}")
            print(f"   Role: {user_data['role']}")
        else:
            print(f"❌ User endpoint failed: {user_response.text}")
    except Exception as e:
        print(f"❌ User request failed: {str(e)}")
    
    # Step 3: Test seller endpoint
    print("\n3️⃣ Testing seller endpoint...")
    try:
        seller_response = requests.get(
            f"{base_url}/api/seller/properties",
            headers=headers
        )
        
        if seller_response.status_code == 200:
            properties = seller_response.json()
            print(f"✅ Seller endpoint works!")
            print(f"   Properties: {len(properties)}")
        else:
            print(f"❌ Seller endpoint failed: {seller_response.text}")
            print(f"   Status: {seller_response.status_code}")
    except Exception as e:
        print(f"❌ Seller request failed: {str(e)}")

if __name__ == "__main__":
    test_jwt_auth()