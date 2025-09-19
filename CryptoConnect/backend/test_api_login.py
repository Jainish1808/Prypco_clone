#!/usr/bin/env python3
"""
Test the actual API login endpoint
"""
import requests
import json

def test_api_login():
    """Test the API login endpoint"""
    print("🧪 Testing API Login Endpoint")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Login with username
    print("\n1️⃣ Testing login with username...")
    try:
        response = requests.post(
            f"{base_url}/api/login",
            headers={"Content-Type": "application/json"},
            json={"username": "admin", "password": "admin123"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login successful!")
            print(f"   Token: {data['access_token'][:50]}...")
            print(f"   User: {data['user']['email']}")
        else:
            print(f"❌ Login failed: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
    
    # Test 2: Login with email
    print("\n2️⃣ Testing login with email...")
    try:
        response = requests.post(
            f"{base_url}/api/login",
            headers={"Content-Type": "application/json"},
            json={"username": "admin@cryptoconnect.com", "password": "admin123"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login successful!")
            print(f"   Token: {data['access_token'][:50]}...")
            print(f"   User: {data['user']['email']}")
        else:
            print(f"❌ Login failed: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

if __name__ == "__main__":
    test_api_login()