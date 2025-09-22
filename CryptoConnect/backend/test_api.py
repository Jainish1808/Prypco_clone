import requests
import json

print("🧪 Testing API endpoints...")

# Test root endpoint
try:
    response = requests.get("http://localhost:8001/")
    print(f"✅ Root endpoint: {response.status_code} - {response.json()}")
except Exception as e:
    print(f"❌ Root endpoint error: {e}")

# Test simple test endpoint
try:
    response = requests.get("http://localhost:8001/api/test-simple")
    print(f"✅ Test-simple endpoint: {response.status_code} - {response.json()}")
except Exception as e:
    print(f"❌ Test-simple endpoint error: {e}")

# Test investor holdings endpoint (should require auth)
try:
    response = requests.get("http://localhost:8001/api/investor/holdings")
    print(f"📝 Holdings endpoint: {response.status_code} - {response.json()}")
except Exception as e:
    print(f"❌ Holdings endpoint error: {e}")

print("🏁 API testing complete!")