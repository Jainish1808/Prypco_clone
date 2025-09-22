#!/usr/bin/env python3
"""
Quick test to verify holdings are now working
"""
import asyncio
import aiohttp

BASE_URL = "http://localhost:8000"

async def test_holdings_fix():
    """Test holdings after fixing the MongoDB query"""
    print("🔧 Testing Holdings Fix")
    print("=" * 40)
    
    async with aiohttp.ClientSession() as session:
        try:
            # Login first
            print("🔑 Logging in...")
            login_data = {
                "username": "jainishjpatel1808@gmail.com",
                "password": "your_password_here"  # You'll need to provide your actual password
            }
            
            async with session.post(f"{BASE_URL}/auth/token", data=login_data) as response:
                if response.status != 200:
                    # Try with just the username if email doesn't work
                    login_data["username"] = "Jainish188"
                    async with session.post(f"{BASE_URL}/auth/token", data=login_data) as retry_response:
                        if retry_response.status != 200:
                            print(f"❌ Login failed: {retry_response.status}")
                            text = await retry_response.text()
                            print(f"Response: {text}")
                            return
                        token_data = await retry_response.json()
                else:
                    token_data = await response.json()
                
                access_token = token_data.get("access_token")
                print(f"✅ Login successful")
            
            # Test holdings endpoint
            headers = {"Authorization": f"Bearer {access_token}"}
            
            print("📊 Testing holdings endpoint...")
            async with session.get(f"{BASE_URL}/api/investor/holdings", headers=headers) as response:
                if response.status != 200:
                    print(f"❌ Holdings failed: {response.status}")
                    text = await response.text()
                    print(f"Response: {text}")
                    return
                
                holdings = await response.json()
                print(f"✅ Holdings endpoint works!")
                print(f"📊 Found {len(holdings)} holdings")
                
                if len(holdings) > 0:
                    for i, holding in enumerate(holdings):
                        print(f"   {i+1}. Property: {holding.get('property_title', 'Unknown')}")
                        print(f"      Tokens: {holding.get('tokenAmount', holding.get('token_amount', 0))}")
                        print(f"      Investment: ${holding.get('totalInvested', holding.get('total_investment', 0))}")
                else:
                    print("   ℹ️ No holdings found")
                    
                    # Let's also check raw transactions
                    print("\n🔍 Checking transactions...")
                    async with session.get(f"{BASE_URL}/api/investor/transactions", headers=headers) as tx_response:
                        if tx_response.status == 200:
                            transactions = await tx_response.json()
                            print(f"   Found {len(transactions)} transactions")
                            for tx in transactions:
                                print(f"   - Type: {tx['transaction_type']}, Status: {tx['status']}, Tokens: {tx['tokens']}")
        
        except Exception as e:
            print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    print("⚠️  Please update the password in the script and run it")
    # asyncio.run(test_holdings_fix())