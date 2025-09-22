#!/usr/bin/env python3

import requests
import json

def verify_portfolio():
    """Verify that the portfolio endpoints are working correctly"""
    
    base_url = "http://localhost:8000"
    
    # Test without authentication first to see if endpoints exist
    print("🔍 Testing API Endpoints")
    print("=" * 50)
    
    # Test holdings endpoint (should return 401 without auth)
    holdings_response = requests.get(f"{base_url}/api/investor/holdings")
    print(f"Holdings endpoint status: {holdings_response.status_code}")
    if holdings_response.status_code == 401:
        print("✅ Holdings endpoint exists (requires authentication)")
    else:
        print(f"❌ Unexpected response: {holdings_response.text}")
    
    # Test transactions endpoint
    transactions_response = requests.get(f"{base_url}/api/investor/transactions")
    print(f"Transactions endpoint status: {transactions_response.status_code}")
    if transactions_response.status_code == 401:
        print("✅ Transactions endpoint exists (requires authentication)")
    else:
        print(f"❌ Unexpected response: {transactions_response.text}")
    
    # Test income statements endpoint
    income_response = requests.get(f"{base_url}/api/investor/income-statements")
    print(f"Income statements endpoint status: {income_response.status_code}")
    if income_response.status_code == 401:
        print("✅ Income statements endpoint exists (requires authentication)")
    else:
        print(f"❌ Unexpected response: {income_response.text}")
    
    print(f"\n📋 Next Steps:")
    print(f"1. Make sure the backend is running on {base_url}")
    print(f"2. Login to your account in the frontend")
    print(f"3. Navigate to 'My Portfolio' in the sidebar")
    print(f"4. Your investment should now appear!")
    
    print(f"\n🔧 If the portfolio is still empty:")
    print(f"1. Check the browser console for any API errors")
    print(f"2. Verify you're logged in as the correct user")
    print(f"3. Make sure the transaction status is 'completed'")

if __name__ == "__main__":
    verify_portfolio()