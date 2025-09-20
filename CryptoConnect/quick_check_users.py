#!/usr/bin/env python3
"""
Quick Database User Check
Simple script to check users without complex imports
"""
import asyncio
import os
import sys

# Set up path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def quick_check():
    try:
        # Import after path setup
        from motor.motor_asyncio import AsyncIOMotorClient
        
        # Connect to MongoDB
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        db = client.cryptoconnect
        users_collection = db.users
        
        print("🔍 Checking Database Users...")
        print("=" * 50)
        
        # Get all users
        users = await users_collection.find().to_list(length=None)
        
        if not users:
            print("❌ No users found in database")
            print("\n💡 Create users first by:")
            print("1. Running the frontend and registering users")
            print("2. Or run: python assign_wallets_to_existing_users.py")
            return
        
        print(f"📊 Found {len(users)} users:\n")
        
        for i, user in enumerate(users, 1):
            print(f"👤 {i}. {user.get('username', 'Unknown')}")
            print(f"   📧 Email: {user.get('email', 'Unknown')}")
            print(f"   🏷️  Role: {user.get('role', 'Unknown')}")
            
            wallet_addr = user.get('xrpl_wallet_address')
            if wallet_addr:
                print(f"   💰 Wallet: ✅ {wallet_addr}")
                print(f"   🔗 Explorer: https://testnet.xrpl.org/accounts/{wallet_addr}")
            else:
                print(f"   💰 Wallet: ❌ Not assigned")
            print()
        
        # Summary
        users_with_wallets = sum(1 for user in users if user.get('xrpl_wallet_address'))
        print(f"📈 Summary: {users_with_wallets}/{len(users)} users have wallets")
        
        if users_with_wallets < len(users):
            print(f"\n🔗 To assign wallets to remaining users:")
            print("Run: .\\assign_wallets_with_env.ps1")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure:")
        print("1. MongoDB is running")
        print("2. Virtual environment is activated")
        print("3. Database exists with users")

if __name__ == "__main__":
    asyncio.run(quick_check())