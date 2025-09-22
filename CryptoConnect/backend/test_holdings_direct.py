import requests
import json

print("🧪 TESTING HOLDINGS ENDPOINT")
print("============================")

# Your JWT token from the Postman screenshot
jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2OGNiZjA1MTUyNjNmYTI3YTQyZWU2MWUiLCJleHAiOjE3MjcwNTQ3NjIsImlhdCI6MTcyNjk2ODM2MiwianRpIjoiVGZlZ3Y4M0lPMml0Y0VjcXBBRzFNdyJ9.gylzqWfl0li2QGNlZJAIMT..."

# Test headers
headers = {
    "Authorization": f"Bearer {jwt_token}",
    "Content-Type": "application/json"
}

print("🔍 Testing endpoint with headers:")
print(f"   Authorization: Bearer {jwt_token[:50]}...")

try:
    response = requests.get("http://localhost:8000/api/investor/holdings", headers=headers)
    print(f"\n📊 Response Status: {response.status_code}")
    print(f"📊 Response Headers: {dict(response.headers)}")
    print(f"📊 Response Body: {response.text}")
    
    if response.status_code == 200:
        try:
            json_data = response.json()
            print(f"📊 JSON Data: {json.dumps(json_data, indent=2)}")
        except:
            print("❌ Could not parse JSON")
    
except Exception as e:
    print(f"❌ Request error: {e}")

print("\n🏁 Test complete!")