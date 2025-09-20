#!/usr/bin/env python3
"""
Manual Wallet Assignment Tool
Allows you to manually assign specific XRP wallets to specific users
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
        "id": 1,
        "address": "rGghB5Kp9YEQhZbxg7Pxm3FGd6gZsytQS8",
        "secret": "sEd7t6iGCmeYpBMW4yQxzK8FnJNpsrh",
        "balance": "10 XRP"
    },
    {
        "id": 2,
        "address": "rnDmRyddBqCDkKBWSnKkzy5ZqtRoVjyDFg", 
        "secret": "sEdSq6vVpKeoxDWARwpxs2KuEe1XPWU",
        "balance": "10 XRP"
    },
    {
        "id": 3,
        "address": "rLB8NiA8MdTS68BXzfu3wwgsZp5uEnyU85",
        "secret": "sEd76oZCyQ4bwMV2SbLNUhULyHLBY29",
        "balance": "10 XRP"
    },
    {
        "id": 4,
        "address": "rJ86bTZkm59iAwV68ZJTq9GdSjBwM5DAw1",
        "secret": "sEdVgnP4k7xVASCmBhkTdgcrH4nYjHw",
        "balance": "10 XRP"
    }
]

async def show_users():
    """Display all users in the database"""
    users = await User.find().to_list()
    
    if not users:
        print("❌ No users found in database")
        return []
    
    print("👥 Available Users:")
    print("-" * 50)
    
    for i, user in enumerate(users, 1):
        wallet_status = "✅ Has wallet" if user.xrpl_wallet_address else "❌ No wallet"
        print(f"{i}. {user.username} ({user.email})")
        print(f"   Role: {user.role.value} | Status: {wallet_status}")
        if user.xrpl_wallet_address:
            print(f"   Current wallet: {user.xrpl_wallet_address}")
        print()
    
    return users

def show_wallets():
    """Display available XRP wallets"""
    print("💰 Available XRP Wallets:")
    print("-" * 50)
    
    for wallet in XRP_WALLETS:
        print(f"{wallet['id']}. Address: {wallet['address']}")
        print(f"   Balance: {wallet['balance']}")
        print(f"   Explorer: https://testnet.xrpl.org/accounts/{wallet['address']}")
        print()

async def assign_wallet_to_user(user, wallet):
    """Assign a specific wallet to a specific user"""
    user.xrpl_wallet_address = wallet["address"]
    user.xrpl_wallet_seed = wallet["secret"]  # In production, encrypt this
    await user.save()
    
    print(f"✅ Successfully assigned wallet to {user.username}")
    print(f"   Address: {wallet['address']}")
    print(f"   Explorer: https://testnet.xrpl.org/accounts/{wallet['address']}")

async def interactive_assignment():
    """Interactive wallet assignment process"""
    print("🎯 Interactive Wallet Assignment")
    print("=" * 60)
    
    users = await show_users()
    if not users:
        return
    
    show_wallets()
    
    assignments = []
    
    while True:
        print("\n🔗 Make an assignment:")
        print("Enter 'done' when finished, or 'quit' to cancel")
        
        # Get user selection
        user_input = input(f"Select user (1-{len(users)}) or 'done'/'quit': ").strip().lower()
        
        if user_input == 'done':
            break
        elif user_input == 'quit':
            print("❌ Assignment cancelled")
            return
        
        try:
            user_index = int(user_input) - 1
            if user_index < 0 or user_index >= len(users):
                print("❌ Invalid user number")
                continue
        except ValueError:
            print("❌ Please enter a valid number")
            continue
        
        selected_user = users[user_index]
        
        # Get wallet selection
        wallet_input = input(f"Select wallet (1-4) for {selected_user.username}: ").strip()
        
        try:
            wallet_index = int(wallet_input) - 1
            if wallet_index < 0 or wallet_index >= 4:
                print("❌ Invalid wallet number")
                continue
        except ValueError:
            print("❌ Please enter a valid number")
            continue
        
        selected_wallet = XRP_WALLETS[wallet_index]
        
        # Check if wallet already assigned
        if any(assignment[1]["id"] == selected_wallet["id"] for assignment in assignments):
            print(f"⚠️  Wallet {selected_wallet['id']} already assigned in this session")
            continue
        
        # Add to assignments
        assignments.append((selected_user, selected_wallet))
        print(f"📝 Queued: {selected_user.username} → Wallet {selected_wallet['id']}")
    
    # Confirm and execute assignments
    if assignments:
        print("\n📋 Assignments to be made:")
        print("-" * 40)
        for user, wallet in assignments:
            print(f"• {user.username} → Wallet {wallet['id']} ({wallet['address']})")
        
        confirm = input("\nProceed with these assignments? (y/N): ").lower().strip()
        
        if confirm == 'y' or confirm == 'yes':
            print("\n🔄 Executing assignments...")
            for user, wallet in assignments:
                await assign_wallet_to_user(user, wallet)
            
            print(f"\n🎉 Successfully assigned {len(assignments)} wallets!")
        else:
            print("❌ Assignments cancelled")

async def quick_assign_all():
    """Quickly assign wallets to first 4 users"""
    users = await User.find().to_list()
    
    if len(users) < 4:
        print(f"❌ Need at least 4 users, found {len(users)}")
        return
    
    print("⚡ Quick Assignment: First 4 users get wallets 1-4")
    print("-" * 50)
    
    for i in range(4):
        user = users[i]
        wallet = XRP_WALLETS[i]
        print(f"{i+1}. {user.username} → Wallet {wallet['id']}")
    
    confirm = input("\nProceed with quick assignment? (y/N): ").lower().strip()
    
    if confirm == 'y' or confirm == 'yes':
        for i in range(4):
            await assign_wallet_to_user(users[i], XRP_WALLETS[i])
        print(f"\n🎉 Quick assignment completed!")
    else:
        print("❌ Quick assignment cancelled")

async def main():
    """Main function"""
    print("🔗 XRP Wallet Assignment Tool")
    print("=" * 60)
    
    await connect_to_mongo()
    
    try:
        while True:
            print("\nChoose an option:")
            print("1. Interactive assignment (choose specific user-wallet pairs)")
            print("2. Quick assignment (first 4 users get wallets 1-4)")
            print("3. View current users and wallets")
            print("4. Exit")
            
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == '1':
                await interactive_assignment()
            elif choice == '2':
                await quick_assign_all()
            elif choice == '3':
                await show_users()
                show_wallets()
            elif choice == '4':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice")
    
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(main())