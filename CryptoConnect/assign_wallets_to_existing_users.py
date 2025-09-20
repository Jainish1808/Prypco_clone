#!/usr/bin/env python3
"""
Assign XRP Wallets to Existing Users
This script assigns your 4 XRP wallets to 4 existing users in the database
"""
import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import connect_to_mongo, close_mongo_connection
from app.models.user import User

# Your 4 XRP wallets from the screenshots
XRP_WALLETS = [
    {
        "address": "rGghB5Kp9YEQhZbxg7Pxm3FGd6gZsytQS8",
        "secret": "sEd7t6iGCmeYpBMW4yQxzK8FnJNpsrh"
    },
    {
        "address": "rnDmRyddBqCDkKBWSnKkzy5ZqtRoVjyDFg", 
        "secret": "sEdSq6vVpKeoxDWARwpxs2KuEe1XPWU"
    },
    {
        "address": "rLB8NiA8MdTS68BXzfu3wwgsZp5uEnyU85",
        "secret": "sEd76oZCyQ4bwMV2SbLNUhULyHLBY29"
    },
    {
        "address": "rJ86bTZkm59iAwV68ZJTq9GdSjBwM5DAw1",
        "secret": "sEdVgnP4k7xVASCmBhkTdgcrH4nYjHw"
    }
]

async def list_existing_users():
    """List all existing users in the database"""
    print("📋 Existing Users in Database:")
    print("=" * 60)
    
    users = await User.find().to_list()
    
    if not users:
        print("❌ No users found in database")
        return []
    
    for i, user in enumerate(users, 1):
        wallet_status = "✅ Has wallet" if user.xrpl_wallet_address else "❌ No wallet"
        print(f"{i}. {user.username} ({user.email})")
        print(f"   Role: {user.role.value}")
        print(f"   Wallet: {wallet_status}")
        if user.xrpl_wallet_address:
            print(f"   Address: {user.xrpl_wallet_address}")
        print()
    
    return users

async def assign_wallets_to_users(users):
    """Assign XRP wallets to the first 4 users"""
    if len(users) < 4:
        print(f"❌ Need at least 4 users, but only found {len(users)}")
        print("Please create more users first")
        return
    
    print("🔗 Assigning XRP wallets to users...")
    print("=" * 60)
    
    # Assign wallets to first 4 users
    for i in range(4):
        user = users[i]
        wallet = XRP_WALLETS[i]
        
        # Update user with wallet information
        user.xrpl_wallet_address = wallet["address"]
        user.xrpl_wallet_seed = wallet["secret"]  # In production, encrypt this
        
        await user.save()
        
        print(f"✅ Assigned wallet {i+1} to {user.username}")
        print(f"   Address: {wallet['address']}")
        print(f"   Explorer: https://testnet.xrpl.org/accounts/{wallet['address']}")
        print()

async def verify_wallet_assignments():
    """Verify that wallets were assigned correctly"""
    print("🔍 Verifying wallet assignments...")
    print("=" * 60)
    
    users = await User.find().to_list()
    
    for user in users:
        if user.xrpl_wallet_address:
            print(f"✅ {user.username}: {user.xrpl_wallet_address}")
        else:
            print(f"❌ {user.username}: No wallet assigned")

async def create_sample_users_if_needed():
    """Create sample users if database is empty"""
    users = await User.find().to_list()
    
    if len(users) >= 4:
        return users
    
    print("📝 Creating sample users for wallet assignment...")
    
    sample_users = [
        {
            "email": "alice@test.com",
            "username": "alice_investor",
            "hashed_password": "$2b$12$LQv3c1yqBwEHxPuNY5Ypm.1pJtMQqvqewf7q/KjSamHEkvseyOw4e",  # password123
            "role": "investor",
            "first_name": "Alice",
            "last_name": "Johnson"
        },
        {
            "email": "bob@test.com", 
            "username": "bob_seller",
            "hashed_password": "$2b$12$LQv3c1yqBwEHxPuNY5Ypm.1pJtMQqvqewf7q/KjSamHEkvseyOw4e",  # password123
            "role": "seller",
            "first_name": "Bob",
            "last_name": "Smith"
        },
        {
            "email": "charlie@test.com",
            "username": "charlie_investor", 
            "hashed_password": "$2b$12$LQv3c1yqBwEHxPuNY5Ypm.1pJtMQqvqewf7q/KjSamHEkvseyOw4e",  # password123
            "role": "investor",
            "first_name": "Charlie",
            "last_name": "Brown"
        },
        {
            "email": "diana@test.com",
            "username": "diana_seller",
            "hashed_password": "$2b$12$LQv3c1yqBwEHxPuNY5Ypm.1pJtMQqvqewf7q/KjSamHEkvseyOw4e",  # password123
            "role": "seller", 
            "first_name": "Diana",
            "last_name": "Wilson"
        }
    ]
    
    created_users = []
    for user_data in sample_users:
        # Check if user already exists
        existing = await User.find_one(User.email == user_data["email"])
        if not existing:
            user = User(**user_data)
            await user.save()
            created_users.append(user)
            print(f"✅ Created user: {user.username}")
        else:
            created_users.append(existing)
            print(f"ℹ️  User already exists: {existing.username}")
    
    return await User.find().to_list()

async def main():
    """Main function to assign wallets to existing users"""
    print("🚀 XRP Wallet Assignment Tool")
    print("=" * 60)
    
    # Connect to database
    await connect_to_mongo()
    
    try:
        # List existing users
        users = await list_existing_users()
        
        # Create sample users if needed
        if len(users) < 4:
            print(f"\n⚠️  Only {len(users)} users found. Creating sample users...")
            users = await create_sample_users_if_needed()
        
        # Show user selection
        print("\n🎯 Select which users to assign wallets to:")
        print("=" * 60)
        
        for i, user in enumerate(users[:4], 1):
            wallet = XRP_WALLETS[i-1]
            print(f"{i}. {user.username} ({user.email}) → Wallet {i}")
            print(f"   Will get: {wallet['address']}")
            print()
        
        # Confirm assignment
        response = input("Proceed with wallet assignment? (y/N): ").lower().strip()
        
        if response == 'y' or response == 'yes':
            await assign_wallets_to_users(users)
            print("\n" + "="*60)
            await verify_wallet_assignments()
            
            print("\n🎉 Wallet assignment completed!")
            print("\n🔗 Your users can now:")
            print("1. Login to the platform")
            print("2. View their assigned XRP wallet")
            print("3. Submit properties (sellers) → Creates real XRP tokens")
            print("4. Buy tokens (investors) → Real blockchain transactions")
            print("5. Transfer tokens to other users")
            
            print("\n🌐 Verify wallets on XRP Testnet Explorer:")
            for i, wallet in enumerate(XRP_WALLETS, 1):
                print(f"   Wallet {i}: https://testnet.xrpl.org/accounts/{wallet['address']}")
                
        else:
            print("❌ Wallet assignment cancelled")
    
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(main())