#!/usr/bin/env python3
"""
Simple test to assign wallets via API
"""
import requests

def test_wallet_assignment():
    try:
        print("🔗 Testing wallet assignment API...")
        
        response = requests.post("http://localhost:8000/api/wallet/assign-to-existing-users")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Assigned {result['wallets_assigned']} wallets")
            
            for i, url in enumerate(result['explorer_links'], 1):
                print(f"Wallet {i}: {url}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_wallet_assignment()