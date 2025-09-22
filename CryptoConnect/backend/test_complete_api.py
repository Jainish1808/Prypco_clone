import requests
import json

print("🧪 COMPLETE API TEST - User Portfolio")
print("=====================================")

BASE_URL = "http://localhost:8001"

# Test 1: Root endpoint
print("\n1. Testing root endpoint...")
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"✅ Root: {response.status_code} - {response.json()}")
except Exception as e:
    print(f"❌ Root error: {e}")

# Test 2: Test endpoint 
print("\n2. Testing simple test endpoint...")
try:
    response = requests.get(f"{BASE_URL}/api/test-simple")
    print(f"✅ Test-simple: {response.status_code} - {response.json()}")
except Exception as e:
    print(f"❌ Test-simple error: {e}")

# Test 3: Holdings without auth (should fail)
print("\n3. Testing holdings without auth (should be 403)...")
try:
    response = requests.get(f"{BASE_URL}/api/investor/holdings")
    print(f"📝 Holdings (no auth): {response.status_code} - {response.json()}")
except Exception as e:
    print(f"❌ Holdings error: {e}")

# Test 4: Login with your user
print("\n4. Logging in...")
login_data = {
    "email": "jaini1808@gmail.com",  # Your email
    "password": "12345"              # Your password
}

try:
    login_response = requests.post(f"{BASE_URL}/api/login", json=login_data)
    print(f"🔑 Login: {login_response.status_code}")
    
    if login_response.status_code == 200:
        login_result = login_response.json()
        token = login_result.get("access_token")
        user_info = login_result.get("user", {})
        print(f"   ✅ Login successful!")
        print(f"   👤 User: {user_info.get('email')} (ID: {user_info.get('id')})")
        print(f"   🔑 Token: {token[:50]}..." if token else "   ❌ No token received")
        
        # Test 5: Holdings with auth
        if token:
            print("\n5. Testing holdings WITH auth...")
            headers = {"Authorization": f"Bearer {token}"}
            
            try:
                holdings_response = requests.get(f"{BASE_URL}/api/investor/holdings", headers=headers)
                print(f"📊 Holdings (with auth): {holdings_response.status_code}")
                
                if holdings_response.status_code == 200:
                    holdings = holdings_response.json()
                    print(f"   ✅ Holdings successful!")
                    print(f"   📦 Holdings data: {json.dumps(holdings, indent=2)}")
                else:
                    print(f"   ❌ Holdings failed: {holdings_response.json()}")
                    
            except Exception as e:
                print(f"   ❌ Holdings request error: {e}")
    else:
        print(f"   ❌ Login failed: {login_response.json()}")
        
except Exception as e:
    print(f"❌ Login error: {e}")

print("\n🏁 Complete API test finished!")