#!/usr/bin/env python3
"""
Test script for XRP token transfers between users
This demonstrates how users can transfer property tokens to each other on XRP testnet
"""

import asyncio
import httpx
import json

# Configuration
BASE_URL = "http://localhost:8000"

# Test users
USER1 = {
    "username": "seller1",
    "password": "testpass123",
    "email": "seller1@example.com",
    "first_name": "Alice",
    "last_name": "Seller"
}

USER2 = {
    "username": "buyer1", 
    "password": "testpass123",
    "email": "buyer1@example.com",
    "first_name": "Bob",
    "last_name": "Buyer"
}

async def register_user(user_data):
    """Register a user and get auth token"""
    async with httpx.AsyncClient() as client:
        # Register
        try:
            await client.post(f"{BASE_URL}/api/auth/register", json=user_data)
        except:
            pass  # User might already exist
        
        # Login
        response = await client.post(
            f"{BASE_URL}/api/auth/login",
            data={"username": user_data["username"], "password": user_data["password"]}
        )
        
        if response.status_code == 200:
            return response.json()["access_token"]
        return None

async def get_user_profile(token):
    """Get user profile including XRP wallet"""
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/auth/profile", headers=headers)
        if response.status_code == 200:
            return response.json()
        return None

async def invest_in_property(token, property_id, tokens_to_buy):
    """Invest in a property (buy initial tokens from issuer)"""
    headers = {"Authorization": f"Bearer {token}"}
    
    investment_data = {
        "property_id": property_id,
        "tokens_to_purchase": tokens_to_buy
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/investor/invest",
            json=investment_data,
            headers=headers,
            timeout=60.0
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Investment failed: {response.text}")
            return None

async def transfer_tokens(sender_token, recipient_address, property_id, amount, memo=None):
    """Transfer tokens between users"""
    headers = {"Authorization": f"Bearer {sender_token}"}
    
    transfer_data = {
        "property_id": property_id,
        "to_address": recipient_address,
        "amount": amount,
        "memo": memo
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/tokens/transfer",
            json=transfer_data,
            headers=headers,
            timeout=60.0
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Transfer failed: {response.text}")
            return None

async def get_property_holders(property_id):
    """Get all holders of a property's tokens"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/tokens/property/{property_id}/holders")
        
        if response.status_code == 200:
            return response.json()
        return None

async def demo_token_transfer():
    """Demonstrate token transfer functionality"""
    print("🔄 STARTING TOKEN TRANSFER DEMONSTRATION")
    print("=" * 50)
    
    # Step 1: Set up users
    print("\n👥 Step 1: Setting up test users")
    
    seller_token = await register_user(USER1)
    buyer_token = await register_user(USER2)
    
    if not seller_token or not buyer_token:
        print("❌ Failed to set up users")
        return
    
    print("✅ Users registered and logged in")
    
    # Get user profiles to get XRP addresses
    seller_profile = await get_user_profile(seller_token)
    buyer_profile = await get_user_profile(buyer_token)
    
    if not seller_profile or not buyer_profile:
        print("❌ Failed to get user profiles")
        return
    
    print(f"👩‍💼 Seller: {seller_profile['username']} - XRP: {seller_profile.get('xrpl_wallet_address', 'N/A')}")
    print(f"👨‍💼 Buyer: {buyer_profile['username']} - XRP: {buyer_profile.get('xrpl_wallet_address', 'N/A')}")
    
    # Step 2: Submit a property (as seller)
    print("\n🏠 Step 2: Creating a tokenized property")
    
    test_property = {
        "title": "Test Property for Transfer Demo",
        "description": "A property to test token transfers",
        "address": "Test Street, Dubai, UAE", 
        "city": "Dubai",
        "country": "UAE",
        "property_type": "apartment",
        "total_value": 1000000.0,  # 1M AED
        "size_sqm": 100.0,  # 100 sqm = 1M tokens
        "bedrooms": 2,
        "bathrooms": 2,
        "monthly_rent": 5000.0
    }
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {seller_token}"}
        response = await client.post(
            f"{BASE_URL}/api/seller/property/submit",
            json=test_property,
            headers=headers,
            timeout=60.0
        )
        
        if response.status_code != 200:
            print(f"❌ Property creation failed: {response.text}")
            return
        
        property_data = response.json()
        property_id = property_data['id']
        
        print(f"✅ Property created and tokenized!")
        print(f"📍 Property ID: {property_id}")
        print(f"🪙 Token Symbol: {property_data.get('token_symbol', 'N/A')}")
        print(f"💰 Total Tokens: {property_data['total_tokens']:,}")
    
    # Step 3: Buyer invests in property
    print(f"\n💰 Step 3: Initial investment (buyer purchases tokens)")
    
    tokens_to_buy = 10000  # 10,000 tokens
    investment = await invest_in_property(buyer_token, property_id, tokens_to_buy)
    
    if not investment:
        print("❌ Initial investment failed")
        return
    
    print(f"✅ Buyer invested successfully!")
    print(f"🪙 Purchased: {tokens_to_buy:,} tokens")
    print(f"💲 Amount: {investment.get('amount', 'N/A')} AED")
    
    # Step 4: Check initial token distribution
    print(f"\n📊 Step 4: Token distribution after initial purchase")
    
    holders = await get_property_holders(property_id)
    if holders:
        print(f"Property: {holders['property_title']}")
        print(f"Token Symbol: {holders['token_symbol']}")
        print(f"Total Supply: {holders['total_supply']}")
        print(f"Number of Holders: {len(holders['holders'])}")
        
        for holder in holders['holders']:
            print(f"  📍 {holder['address']}: {holder['balance']:,} tokens")
    
    # Step 5: Transfer tokens between users
    print(f"\n🔄 Step 5: Transferring tokens from buyer to seller")
    
    if not buyer_profile.get('xrpl_wallet_address'):
        print("❌ Buyer doesn't have XRP wallet address")
        return
    
    transfer_amount = 1000  # Transfer 1,000 tokens back to seller
    transfer_result = await transfer_tokens(
        buyer_token,
        seller_profile.get('xrpl_wallet_address'),
        property_id,
        transfer_amount,
        "Partial token transfer demonstration"
    )
    
    if transfer_result:
        print(f"✅ Token transfer successful!")
        print(f"🔄 Transferred: {transfer_amount:,} tokens")
        print(f"📤 From: {transfer_result['from_address']}")
        print(f"📥 To: {transfer_result['to_address']}")
        print(f"🔗 TX Hash: {transfer_result['tx_hash']}")
        print(f"🌐 Explorer: {transfer_result['explorer_url']}")
    else:
        print("❌ Token transfer failed")
        return
    
    # Step 6: Check final token distribution
    print(f"\n📊 Step 6: Final token distribution after transfer")
    
    await asyncio.sleep(3)  # Wait for ledger to update
    
    holders = await get_property_holders(property_id)
    if holders:
        print(f"Updated token distribution:")
        for holder in holders['holders']:
            user_info = holder.get('user_info', {})
            name = user_info.get('name', 'Unknown') if user_info else 'Unknown'
            print(f"  📍 {holder['address']} ({name}): {holder['balance']:,} tokens")
    
    print(f"\n🎉 TOKEN TRANSFER DEMONSTRATION COMPLETED!")
    print("=" * 50)
    print("✅ Successfully demonstrated:")
    print("  - Property tokenization on XRP Ledger")
    print("  - Initial token purchase from issuer")
    print("  - Peer-to-peer token transfers")
    print("  - Real-time token holder tracking")
    print("  - XRP testnet explorer integration")
    
    if transfer_result:
        print(f"\n🔗 View the transfer on XRP Explorer:")
        print(f"   {transfer_result['explorer_url']}")

if __name__ == "__main__":
    asyncio.run(demo_token_transfer())