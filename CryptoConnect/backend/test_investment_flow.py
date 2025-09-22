#!/usr/bin/env python3
"""
Test the complete investment flow for the User database
"""
import asyncio
import aiohttp
import json

BASE_URL = "http://127.0.0.1:8000"

async def test_complete_investment_flow():
    """Test the complete investment flow"""
    print("🧪 Testing Complete Investment Flow")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Step 1: Login as investor
        print("\n1️⃣ Logging in as test investor...")
        login_data = {
            "username": "investor@test.com",
            "password": "testpass123"
        }
        
        async with session.post(f"{BASE_URL}/auth/token", data=login_data) as response:
            if response.status != 200:
                print(f"❌ Login failed: {response.status}")
                text = await response.text()
                print(f"Response: {text}")
                return
            
            token_data = await response.json()
            access_token = token_data.get("access_token")
            print(f"✅ Login successful, token: {access_token[:20]}...")
        
        # Set headers for authenticated requests
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Step 2: Check available properties
        print("\n2️⃣ Checking available properties...")
        async with session.get(f"{BASE_URL}/properties/", headers=headers) as response:
            if response.status != 200:
                print(f"❌ Properties fetch failed: {response.status}")
                text = await response.text()
                print(f"Response: {text}")
                return
            
            properties = await response.json()
            print(f"✅ Found {len(properties)} properties")
            
            if not properties:
                print("❌ No properties available for investment")
                return
            
            # Use the first property for testing
            test_property = properties[0]
            property_id = test_property["id"]
            print(f"📊 Test property: {test_property['title']}")
            print(f"   💰 Token price: ${test_property['token_price']}")
            print(f"   🏠 Property ID: {property_id}")
        
        # Step 3: Check portfolio before investment
        print("\n3️⃣ Checking portfolio before investment...")
        async with session.get(f"{BASE_URL}/investor/holdings", headers=headers) as response:
            if response.status != 200:
                print(f"❌ Holdings fetch failed: {response.status}")
                text = await response.text()
                print(f"Response: {text}")
                return
            
            holdings_before = await response.json()
            print(f"✅ Current holdings: {len(holdings_before)} properties")
            
            for holding in holdings_before:
                print(f"   🏠 {holding['property_title']}: {holding['tokens_owned']} tokens")
        
        # Step 4: Make an investment
        print("\n4️⃣ Making investment...")
        investment_data = {
            "property_id": property_id,
            "tokens_to_buy": 10,
            "payment_method": "xrp"
        }
        
        async with session.post(f"{BASE_URL}/properties/{property_id}/invest", 
                              headers=headers, 
                              json=investment_data) as response:
            if response.status != 200:
                print(f"❌ Investment failed: {response.status}")
                text = await response.text()
                print(f"Response: {text}")
                return
            
            investment_result = await response.json()
            print(f"✅ Investment successful!")
            print(f"   📄 Transaction ID: {investment_result.get('transaction_id', 'N/A')}")
            print(f"   💰 Amount: {investment_result.get('total_amount', 'N/A')}")
            print(f"   🪙 Tokens: {investment_result.get('tokens_purchased', 'N/A')}")
        
        # Step 5: Check portfolio after investment
        print("\n5️⃣ Checking portfolio after investment...")
        async with session.get(f"{BASE_URL}/investor/holdings", headers=headers) as response:
            if response.status != 200:
                print(f"❌ Holdings fetch failed: {response.status}")
                text = await response.text()
                print(f"Response: {text}")
                return
            
            holdings_after = await response.json()
            print(f"✅ Updated holdings: {len(holdings_after)} properties")
            
            for holding in holdings_after:
                print(f"   🏠 {holding['property_title']}: {holding['tokens_owned']} tokens")
                print(f"      💰 Total value: ${holding['total_value']}")
        
        # Step 6: Check transaction history  
        print("\n6️⃣ Checking transaction history...")
        async with session.get(f"{BASE_URL}/investor/transactions", headers=headers) as response:
            if response.status != 200:
                print(f"❌ Transactions fetch failed: {response.status}")
                text = await response.text() 
                print(f"Response: {text}")
                return
            
            transactions = await response.json()
            print(f"✅ Transaction history: {len(transactions)} transactions")
            
            for txn in transactions[-3:]:  # Show last 3 transactions
                print(f"   📄 {txn['type']}: ${txn['amount']}")
                print(f"      🏠 Property: {txn.get('property_title', 'N/A')}")
                print(f"      ⏰ Date: {txn['created_at']}")
    
    print("\n" + "=" * 60)
    print("🎉 Complete investment flow test completed!")

if __name__ == "__main__":
    asyncio.run(test_complete_investment_flow())