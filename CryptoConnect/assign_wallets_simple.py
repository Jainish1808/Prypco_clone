#!/usr/bin/env python3
"""
Simple script to assign your 4 XRP wallets to existing users
Just run this after starting your backend server
"""
import requests
import json

def assign_wallets():
    """Call the API to assign wallets to existing users"""
    try:
        print("🔗 Assigning XRP wallets to existing users...")
        
        # Call the API endpoint
        response = requests.post("http://localhost:8000/api/wallet/assign-to-existing-users")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"📊 Assigned {result['wallets_assigned']} wallets")
            
            print("\n🔗 Your wallets on XRP Testnet Explorer:")
            for i, url in enumerate(result['explorer_links'], 1):
                print(f"   Wallet {i}: {url}")
                
            print("\n🎉 Users can now:")
            print("• Login to see their assigned XRP wallet")
            print("• Submit properties → Creates real XRP tokens")
            print("• Buy/transfer tokens → Real blockchain transactions")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server")
        print("💡 Make sure backend is running on http://localhost:8000")
        print("Start with: cd backend && python -m uvicorn app.main:app --reload")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    assign_wallets()