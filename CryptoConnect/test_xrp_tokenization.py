#!/usr/bin/env python3
"""
Test script for enhanced XRP Ledger tokenization
This script demonstrates how property tokens are created on XRP testnet
and how they can be viewed on the testnet explorer.
"""

import asyncio
import httpx
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER_CREDENTIALS = {
    "username": "testuser",
    "password": "testpass123",
    "email": "testuser@example.com",
    "first_name": "Test",
    "last_name": "User"
}

TEST_PROPERTY = {
    "title": "Luxury Villa Dubai Marina",
    "description": "A beautiful luxury villa with stunning marina views",
    "address": "Dubai Marina Walk, Dubai, UAE",
    "city": "Dubai",
    "country": "UAE",
    "property_type": "villa",
    "total_value": 5000000.0,  # 5M AED
    "size_sqm": 500.0,  # 500 sqm
    "bedrooms": 4,
    "bathrooms": 4,
    "parking_spaces": 2,
    "year_built": 2020,
    "monthly_rent": 25000.0,
    "images": []
}

async def register_and_login():
    """Register a test user and get auth token"""
    async with httpx.AsyncClient() as client:
        # Register user
        try:
            register_response = await client.post(
                f"{BASE_URL}/api/auth/register",
                json=TEST_USER_CREDENTIALS
            )
            print(f"Registration response: {register_response.status_code}")
            if register_response.status_code not in [200, 400]:  # 400 might mean user already exists
                print(f"Registration failed: {register_response.text}")
        except Exception as e:
            print(f"Registration error: {e}")
        
        # Login
        login_response = await client.post(
            f"{BASE_URL}/api/auth/login",
            data={
                "username": TEST_USER_CREDENTIALS["username"],
                "password": TEST_USER_CREDENTIALS["password"]
            }
        )
        
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            print(f"✅ Login successful")
            return token
        else:
            print(f"❌ Login failed: {login_response.text}")
            return None

async def submit_property(token):
    """Submit a test property"""
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/seller/property/submit",
            json=TEST_PROPERTY,
            headers=headers,
            timeout=60.0  # Increase timeout for tokenization
        )
        
        if response.status_code == 200:
            property_data = response.json()
            print(f"✅ Property submitted successfully!")
            print(f"📍 Property ID: {property_data['id']}")
            print(f"📊 Total Tokens: {property_data['total_tokens']:,}")
            print(f"💲 Token Price: {property_data['token_price']:.6f} AED")
            return property_data
        else:
            print(f"❌ Property submission failed: {response.text}")
            return None

async def get_tokenization_details(token, property_id):
    """Get detailed tokenization information"""
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/api/seller/property/{property_id}/tokenization",
            headers=headers
        )
        
        if response.status_code == 200:
            details = response.json()
            print(f"\n🔍 TOKENIZATION DETAILS:")
            print(f"Property: {details['title']}")
            print(f"Status: {details['status']}")
            print(f"Tokenized: {details['tokenized']}")
            
            if details['tokenized']:
                token_details = details['token_details']
                print(f"\n🪙 TOKEN INFORMATION:")
                print(f"Token Symbol: {token_details['token_symbol']}")
                print(f"Total Tokens: {token_details['total_tokens']:,}")
                print(f"Token Price: {token_details['token_price']:.6f} AED")
                print(f"Tokens Available: {token_details['tokens_available']:,}")
                
                xrpl = token_details['xrpl_details']
                print(f"\n🔗 XRP LEDGER INFORMATION:")
                print(f"Network: {xrpl['network']}")
                print(f"Issuer Address: {xrpl['issuer_address']}")
                print(f"Creation Tx: {xrpl['creation_tx_hash']}")
                print(f"📊 Transaction Explorer: {xrpl['explorer_url']}")
                print(f"🏦 Issuer Account Explorer: {xrpl['issuer_explorer_url']}")
                
                if 'live_data' in token_details:
                    live = token_details['live_data']
                    print(f"\n📡 LIVE LEDGER DATA:")
                    print(f"Verified on Ledger: {live.get('verified_on_ledger', 'N/A')}")
                    print(f"Live Total Supply: {live.get('live_total_supply', 'N/A')}")
                    print(f"Current Holders: {live.get('current_holders', 'N/A')}")
                
                return xrpl
            
            return None
        else:
            print(f"❌ Failed to get tokenization details: {response.text}")
            return None

async def get_user_tokens(token):
    """Get user's XRP token holdings"""
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/api/tokens/my-tokens",
            headers=headers
        )
        
        if response.status_code == 200:
            tokens = response.json()
            print(f"\n💼 YOUR TOKEN PORTFOLIO:")
            print(f"XRP Address: {tokens['xrpl_address']}")
            print(f"Total Tokens: {tokens['total_tokens']:,}")
            
            for token_info in tokens['tokens']:
                print(f"\n🪙 Token: {token_info['currency']}")
                print(f"  Balance: {token_info['balance']:,.0f}")
                print(f"  Property: {token_info.get('property_title', 'Unknown')}")
                print(f"  Issuer: {token_info['issuer']}")
            
            return tokens
        else:
            print(f"❌ Failed to get user tokens: {response.text}")
            return None

async def verify_token_on_ledger(token_symbol, issuer_address):
    """Verify token exists on XRP Ledger"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/api/tokens/verify/{token_symbol}?issuer_address={issuer_address}"
        )
        
        if response.status_code == 200:
            verification = response.json()
            print(f"\n🔍 TOKEN VERIFICATION:")
            print(f"Token Symbol: {verification['token_symbol']}")
            print(f"Exists on Ledger: {verification['exists']}")
            print(f"Total Supply: {verification.get('total_supply', 'N/A')}")
            print(f"Number of Holders: {len(verification.get('holders', []))}")
            
            if verification.get('property_info'):
                prop_info = verification['property_info']
                print(f"\n🏠 ASSOCIATED PROPERTY:")
                print(f"Title: {prop_info['title']}")
                print(f"Address: {prop_info['address']}")
                print(f"Value: {prop_info['total_value']:,} AED")
                print(f"Creation Tx: {prop_info['creation_tx']}")
                print(f"Explorer: {prop_info['explorer_url']}")
            
            return verification
        else:
            print(f"❌ Token verification failed: {response.text}")
            return None

async def main():
    """Main test function"""
    print("🚀 STARTING XRP LEDGER TOKENIZATION TEST")
    print("=" * 50)
    
    # Step 1: Register and login
    print("\n📝 Step 1: User Registration & Login")
    token = await register_and_login()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    # Step 2: Submit property
    print("\n🏠 Step 2: Property Submission & Tokenization")
    property_data = await submit_property(token)
    if not property_data:
        print("❌ Cannot proceed without property")
        return
    
    property_id = property_data['id']
    
    # Wait a moment for tokenization to complete
    print("⏳ Waiting for tokenization to complete...")
    await asyncio.sleep(5)
    
    # Step 3: Get tokenization details
    print("\n🔍 Step 3: Tokenization Details")
    xrpl_details = await get_tokenization_details(token, property_id)
    
    # Step 4: Get user tokens
    print("\n💼 Step 4: User Token Portfolio")
    user_tokens = await get_user_tokens(token)
    
    # Step 5: Verify token on ledger
    if xrpl_details:
        print("\n✅ Step 5: Ledger Verification")
        await verify_token_on_ledger(
            xrpl_details['issuer_address'].split('.')[-1],  # Get token symbol from issuer
            xrpl_details['issuer_address']
        )
    
    print("\n🎉 TEST COMPLETED!")
    print("=" * 50)
    print("Your property has been tokenized on XRP Testnet!")
    print("You can now view the tokens on the XRP Ledger Explorer.")
    
    if xrpl_details:
        print(f"\n🔗 Quick Links:")
        print(f"Transaction: {xrpl_details['explorer_url']}")
        print(f"Issuer Account: {xrpl_details['issuer_explorer_url']}")
        print(f"Testnet Explorer: https://testnet.xrpl.org/")

if __name__ == "__main__":
    asyncio.run(main())