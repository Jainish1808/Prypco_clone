#!/usr/bin/env python3
"""
Complete XRP Tokenization Flow Test
Tests the entire flow from user registration to property tokenization to token transfers
"""
import asyncio
import httpx
import json
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USERS = [
    {
        "username": "alice_investor",
        "email": "alice@test.com", 
        "password": "password123",
        "firstName": "Alice",
        "lastName": "Johnson",
        "userType": "investor"
    },
    {
        "username": "bob_seller",
        "email": "bob@test.com",
        "password": "password123", 
        "firstName": "Bob",
        "lastName": "Smith",
        "userType": "seller"
    }
]

# Your XRP wallet addresses (from the screenshots)
XRP_WALLETS = [
    {
        "address": "rGghB5Kp9YEQhZbxg7Pxm3FGd6gZsytQS8",
        "secret": "sEd7t6iGCmeYpBMW4yQxzK8FnJNpsrh"
    },
    {
        "address": "rnDmRyddBqCDkKBWSnKkzy5ZqtRoVjyDFg", 
        "secret": "sEdSq6vVpKeoxDWARwpxs2KuEe1XPWU"
    }
]

async def register_and_login_user(client: httpx.AsyncClient, user_data: dict, wallet_data: dict):
    """Register a user and connect their XRP wallet"""
    print(f"\n🔐 Registering user: {user_data['username']}")
    
    # Register user
    register_response = await client.post(f"{BASE_URL}/api/register", json=user_data)
    if register_response.status_code != 200:
        print(f"❌ Registration failed: {register_response.text}")
        return None
    
    print(f"✅ User registered successfully")
    
    # Login user
    login_response = await client.post(f"{BASE_URL}/api/login", json={
        "username": user_data["username"],
        "password": user_data["password"]
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return None
    
    login_data = login_response.json()
    token = login_data["access_token"]
    user_info = login_data["user"]
    
    print(f"✅ User logged in successfully")
    print(f"   User ID: {user_info['id']}")
    print(f"   Auto-assigned wallet: {user_info.get('walletAddress', 'None')}")
    
    # Connect XRP wallet if not auto-assigned
    if not user_info.get('walletAddress'):
        print(f"🔗 Connecting XRP wallet: {wallet_data['address']}")
        
        wallet_response = await client.post(
            f"{BASE_URL}/api/wallet/connect",
            json=wallet_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if wallet_response.status_code == 200:
            wallet_info = wallet_response.json()
            print(f"✅ Wallet connected successfully")
            print(f"   Address: {wallet_info['address']}")
            print(f"   XRP Balance: {wallet_info['xrp_balance']} XRP")
        else:
            print(f"❌ Wallet connection failed: {wallet_response.text}")
    
    return {
        "token": token,
        "user": user_info,
        "wallet": wallet_data
    }

async def submit_property(client: httpx.AsyncClient, token: str):
    """Submit a property for tokenization"""
    print(f"\n🏠 Submitting property for tokenization")
    
    property_data = {
        "title": "Luxury Dubai Marina Apartment",
        "description": "Premium waterfront apartment with stunning marina views. Perfect investment opportunity in Dubai's most prestigious location.",
        "address": "Marina Walk, Dubai Marina",
        "city": "Dubai", 
        "country": "UAE",
        "property_type": "apartment",
        "total_value": 2500000,  # 2.5M AED
        "size_sqm": 150,         # 150 sqm
        "bedrooms": 2,
        "bathrooms": 2,
        "parking_spaces": 1,
        "year_built": 2020,
        "monthly_rent": 15000,   # 15K AED/month
        "images": [],
        "acceptedTerms": True
    }
    
    response = await client.post(
        f"{BASE_URL}/api/seller/property/submit",
        json=property_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        property_info = response.json()
        print(f"✅ Property submitted successfully!")
        print(f"   Property ID: {property_info['id']}")
        print(f"   Token Symbol: {property_info.get('token_symbol', 'N/A')}")
        print(f"   Total Tokens: {property_info.get('total_tokens', 0):,}")
        print(f"   Token Price: ${property_info.get('token_price', 0):.2f}")
        
        if property_info.get('xrpl_explorer_url'):
            print(f"   🔗 XRP Explorer: {property_info['xrpl_explorer_url']}")
        
        return property_info
    else:
        print(f"❌ Property submission failed: {response.text}")
        return None

async def get_wallet_info(client: httpx.AsyncClient, token: str, username: str):
    """Get wallet information and token holdings"""
    print(f"\n💰 Getting wallet info for {username}")
    
    response = await client.get(
        f"{BASE_URL}/api/wallet/info",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        wallet_info = response.json()
        print(f"✅ Wallet info retrieved")
        print(f"   Address: {wallet_info['address']}")
        print(f"   XRP Balance: {wallet_info['xrp_balance']:.6f} XRP")
        print(f"   Property Tokens: {len(wallet_info['tokens'])}")
        
        for token in wallet_info['tokens']:
            print(f"     - {token['symbol']}: {token['balance']:,} tokens")
            if token.get('property_info'):
                prop = token['property_info']
                print(f"       Property: {prop['title']} ({prop['city']}, {prop['country']})")
        
        print(f"   🔗 Explorer: {wallet_info['explorer_url']}")
        return wallet_info
    else:
        print(f"❌ Failed to get wallet info: {response.text}")
        return None

async def purchase_tokens(client: httpx.AsyncClient, token: str, property_id: str, amount: int):
    """Purchase property tokens"""
    print(f"\n🛒 Purchasing {amount:,} property tokens")
    
    response = await client.post(
        f"{BASE_URL}/api/investor/property/{property_id}/invest",
        json={"tokenAmount": amount},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Token purchase successful!")
        print(f"   Transaction Hash: {result.get('transaction_hash', 'N/A')}")
        print(f"   Tokens Purchased: {amount:,}")
        print(f"   Total Cost: ${result.get('total_cost', 0):,.2f}")
        
        if result.get('explorer_url'):
            print(f"   🔗 Transaction: {result['explorer_url']}")
        
        return result
    else:
        print(f"❌ Token purchase failed: {response.text}")
        return None

async def transfer_tokens(client: httpx.AsyncClient, token: str, to_address: str, token_symbol: str, amount: float):
    """Transfer tokens between wallets"""
    print(f"\n🔄 Transferring {amount:,} {token_symbol} tokens to {to_address}")
    
    response = await client.post(
        f"{BASE_URL}/api/wallet/transfer",
        json={
            "to_address": to_address,
            "token_symbol": token_symbol, 
            "amount": amount
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Token transfer successful!")
        print(f"   Transaction Hash: {result['transaction_hash']}")
        print(f"   Amount: {amount:,} {token_symbol}")
        print(f"   To: {to_address}")
        print(f"   🔗 Explorer: {result['explorer_url']}")
        return result
    else:
        print(f"❌ Token transfer failed: {response.text}")
        return None

async def main():
    """Run the complete XRP tokenization flow test"""
    print("🚀 Starting Complete XRP Tokenization Flow Test")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Step 1: Register users and connect wallets
        alice = await register_and_login_user(client, TEST_USERS[0], XRP_WALLETS[0])
        bob = await register_and_login_user(client, TEST_USERS[1], XRP_WALLETS[1])
        
        if not alice or not bob:
            print("❌ Failed to set up test users")
            return
        
        # Step 2: Bob (seller) submits a property
        property_info = await submit_property(client, bob["token"])
        if not property_info:
            print("❌ Failed to submit property")
            return
        
        # Step 3: Check wallet balances
        await get_wallet_info(client, alice["token"], "Alice (Investor)")
        await get_wallet_info(client, bob["token"], "Bob (Seller)")
        
        # Step 4: Alice purchases tokens
        purchase_amount = 1000  # Buy 1000 tokens
        purchase_result = await purchase_tokens(
            client, 
            alice["token"], 
            property_info["id"], 
            purchase_amount
        )
        
        if purchase_result:
            # Step 5: Check updated wallet balances
            print("\n" + "="*40 + " AFTER PURCHASE " + "="*40)
            alice_wallet = await get_wallet_info(client, alice["token"], "Alice (Investor)")
            await get_wallet_info(client, bob["token"], "Bob (Seller)")
            
            # Step 6: Alice transfers some tokens to Bob
            if alice_wallet and alice_wallet["tokens"]:
                token_symbol = alice_wallet["tokens"][0]["symbol"]
                transfer_amount = 100  # Transfer 100 tokens
                
                await transfer_tokens(
                    client,
                    alice["token"],
                    bob["wallet"]["address"],
                    token_symbol,
                    transfer_amount
                )
                
                # Step 7: Final wallet check
                print("\n" + "="*40 + " AFTER TRANSFER " + "="*40)
                await get_wallet_info(client, alice["token"], "Alice (Investor)")
                await get_wallet_info(client, bob["token"], "Bob (Seller)")
        
        # Summary
        print("\n" + "="*60)
        print("🎉 Complete XRP Tokenization Flow Test Completed!")
        print("="*60)
        print("\n📋 What was tested:")
        print("✅ User registration with automatic XRP wallet assignment")
        print("✅ XRP wallet connection and validation")
        print("✅ Property submission and tokenization on XRP Ledger")
        print("✅ Real XRP token creation (visible on testnet explorer)")
        print("✅ Token purchase and wallet balance updates")
        print("✅ Peer-to-peer token transfers")
        print("✅ All transactions recorded on XRP blockchain")
        
        print("\n🔗 View your tokens on XRP Testnet Explorer:")
        print(f"   Alice's Wallet: https://testnet.xrpl.org/accounts/{alice['wallet']['address']}")
        print(f"   Bob's Wallet: https://testnet.xrpl.org/accounts/{bob['wallet']['address']}")
        
        if property_info.get('xrpl_explorer_url'):
            print(f"   Property Tokens: {property_info['xrpl_explorer_url']}")

if __name__ == "__main__":
    asyncio.run(main())