#!/usr/bin/env python3
"""
Check Database Users
This script shows all users in your database and their current wallet status
"""
import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import connect_to_mongo, close_mongo_connection
from app.models.user import User

async def check_users():
    """Check all users in the database"""
    print("🔍 Checking Database Users")
    print("=" * 60)
    
    # Connect to database
    await connect_to_mongo()
    
    try:
        users = await User.find().to_list()
        
        if not users:
            print("❌ No users found in database")
            print("\nTo create test users, run:")
            print("python assign_wallets_to_existing_users.py")
            return
        
        print(f"📊 Found {len(users)} users in database:\n")
        
        for i, user in enumerate(users, 1):
            print(f"👤 User {i}: {user.username}")
            print(f"   📧 Email: {user.email}")
            print(f"   🏷️  Role: {user.role.value}")
            print(f"   ✅ Active: {user.is_active}")
            print(f"   🔐 KYC: {'✅ Verified' if user.is_kyc_verified else '❌ Pending'}")
            
            # Wallet status
            if user.xrpl_wallet_address:
                print(f"   💰 Wallet: ✅ Connected")
                print(f"   📍 Address: {user.xrpl_wallet_address}")
                print(f"   🔗 Explorer: https://testnet.xrpl.org/accounts/{user.xrpl_wallet_address}")
            else:
                print(f"   💰 Wallet: ❌ Not assigned")
            
            print(f"   📅 Created: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print()
        
        # Summary
        users_with_wallets = sum(1 for user in users if user.xrpl_wallet_address)
        users_without_wallets = len(users) - users_with_wallets
        
        print("📈 Summary:")
        print(f"   Total Users: {len(users)}")
        print(f"   With Wallets: {users_with_wallets}")
        print(f"   Without Wallets: {users_without_wallets}")
        
        if users_without_wallets > 0:
            print(f"\n💡 To assign XRP wallets to users without wallets:")
            print("python assign_wallets_to_existing_users.py")
    
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(check_users())