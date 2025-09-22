#!/usr/bin/env python3

import requests
import json

def test_user_holdings():
    """Test the user holdings endpoint with the actual user token"""
    
    # First, login to get the token
    login_data = {
        "username": "Jainish188",  # From the logs
        "password": "your_password_here"  # You'll need to provide this
    }
    
    print("🔐 Testing login...")
    login_response = requests.post("http://localhost:8000/api/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return
    
    login_result = login_response.json()
    token = login_result["access_token"]
    user = login_result["user"]
    
    print(f"✅ Login successful!")
    print(f"   User ID: {user['id']}")
    print(f"   Username: {user['username']}")
    print(f"   Email: {user['email']}")
    print(f"   User Type: {user['userType']}")
    
    # Test the holdings endpoint
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n🔍 Testing holdings endpoint...")
    holdings_response = requests.get("http://localhost:8000/api/investor/holdings", headers=headers)
    
    print(f"Holdings response status: {holdings_response.status_code}")
    
    if holdings_response.status_code == 200:
        holdings = holdings_response.json()
        print(f"✅ Holdings retrieved successfully!")
        print(f"   Number of holdings: {len(holdings)}")
        
        for i, holding in enumerate(holdings):
            print(f"\n   Holding {i+1}:")
            print(f"     Property: {holding.get('property_title', 'N/A')}")
            print(f"     Tokens: {holding.get('tokens', 0)}")
            print(f"     Investment: ${holding.get('total_investment', 0)}")
            print(f"     Current Value: ${holding.get('current_value', 0)}")
    else:
        print(f"❌ Holdings request failed: {holdings_response.status_code}")
        print(f"Response: {holdings_response.text}")
    
    # Test the transactions endpoint
    print(f"\n🔍 Testing transactions endpoint...")
    transactions_response = requests.get("http://localhost:8000/api/investor/transactions", headers=headers)
    
    print(f"Transactions response status: {transactions_response.status_code}")
    
    if transactions_response.status_code == 200:
        transactions = transactions_response.json()
        print(f"✅ Transactions retrieved successfully!")
        print(f"   Number of transactions: {len(transactions)}")
        
        for i, tx in enumerate(transactions[:3]):  # Show first 3
            print(f"\n   Transaction {i+1}:")
            print(f"     Type: {tx.get('transaction_type', 'N/A')}")
            print(f"     Status: {tx.get('status', 'N/A')}")
            print(f"     Amount: ${tx.get('amount', 0)}")
            print(f"     Tokens: {tx.get('tokens', 0)}")
            print(f"     Property ID: {tx.get('property_id', 'N/A')}")
    else:
        print(f"❌ Transactions request failed: {transactions_response.status_code}")
        print(f"Response: {transactions_response.text}")

if __name__ == "__main__":
    print("🧪 Testing User Holdings API")
    print("=" * 50)
    print("Note: You need to update the password in the script")
    print("=" * 50)
    # test_user_holdings()  # Uncomment after setting password