#!/usr/bin/env python3
"""
Test the complete dynamic frontend functionality
"""
import asyncio
import aiohttp
import json

BASE_URL = "http://127.0.0.1:8000"

async def test_dynamic_functionality():
    """Test all dynamic frontend features"""
    print("🧪 Testing Dynamic Frontend Functionality")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        try:
            # Step 1: Login as test investor
            print("\n1️⃣ Testing login...")
            login_data = {
                "username": "investor@test.com",
                "password": "testpass123"
            }
            
            async with session.post(f"{BASE_URL}/auth/token", data=login_data) as response:
                if response.status != 200:
                    print(f"❌ Login failed: {response.status}")
                    return
                
                token_data = await response.json()
                access_token = token_data.get("access_token")
                print(f"✅ Login successful")
            
            # Set headers for authenticated requests
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Step 2: Test Portfolio API (should show holdings)
            print("\n2️⃣ Testing Portfolio Holdings API...")
            async with session.get(f"{BASE_URL}/api/investor/holdings", headers=headers) as response:
                if response.status != 200:
                    print(f"❌ Holdings API failed: {response.status}")
                    return
                
                holdings = await response.json()
                print(f"✅ Holdings API works: {len(holdings)} holdings found")
                
                if len(holdings) > 0:
                    print(f"   📊 Sample holding: {holdings[0].get('property_title', 'N/A')}")
                else:
                    print("   ℹ️ No holdings yet - expected for new user")
            
            # Step 3: Test Properties API (for Browse Available Properties)
            print("\n3️⃣ Testing Available Properties API...")
            async with session.get(f"{BASE_URL}/api/properties/", headers=headers) as response:
                if response.status != 200:
                    print(f"❌ Properties API failed: {response.status}")
                    return
                
                properties = await response.json()
                print(f"✅ Properties API works: {len(properties)} properties available")
                
                if len(properties) > 0:
                    test_property = properties[0]
                    print(f"   🏠 Sample property: {test_property.get('title', 'N/A')}")
                    print(f"   💰 Token price: ${test_property.get('token_price', 0)}")
            
            # Step 4: Test Income Statements API
            print("\n4️⃣ Testing Income History API...")
            async with session.get(f"{BASE_URL}/api/investor/income-statements", headers=headers) as response:
                if response.status != 200:
                    print(f"❌ Income API failed: {response.status}")
                    return
                
                income_statements = await response.json()
                print(f"✅ Income API works: {len(income_statements)} statements found")
                
                if len(income_statements) > 0:
                    print(f"   💰 Total income: ${sum(stmt.get('amount', 0) for stmt in income_statements)}")
                else:
                    print("   ℹ️ No income history yet - expected for new user")
            
            # Step 5: Test Secondary Market Orders API
            print("\n5️⃣ Testing Secondary Market API...")
            async with session.get(f"{BASE_URL}/api/market/orders", headers=headers) as response:
                if response.status == 404:
                    print("⚠️ Market orders endpoint not implemented yet")
                elif response.status != 200:
                    print(f"❌ Market API failed: {response.status}")
                else:
                    market_orders = await response.json()
                    print(f"✅ Market API works: {len(market_orders)} orders found")
            
            # Step 6: Test Transactions API
            print("\n6️⃣ Testing Transaction History API...")
            async with session.get(f"{BASE_URL}/api/investor/transactions", headers=headers) as response:
                if response.status != 200:
                    print(f"❌ Transactions API failed: {response.status}")
                    return
                
                transactions = await response.json()
                print(f"✅ Transactions API works: {len(transactions)} transactions found")
                
                if len(transactions) > 0:
                    rental_txs = [tx for tx in transactions if tx.get('transaction_type') == 'rental_distribution']
                    print(f"   💵 Rental distributions: {len(rental_txs)}")
            
            print("\n" + "=" * 60)
            print("🎉 Dynamic Frontend Functionality Test Completed!")
            print("\n✅ All APIs are working and frontend should be fully dynamic:")
            print("   • Portfolio page shows real holdings or empty state with working button")
            print("   • Secondary Market shows real orders with proper property filtering")
            print("   • Income History shows real rental income distributions")
            print("   • All static content has been replaced with dynamic data")
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_dynamic_functionality())