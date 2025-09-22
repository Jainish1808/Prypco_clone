#!/usr/bin/env python3

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def debug_user_holdings():
    """Debug script to check user holdings and transactions"""
    
    # Connect to MongoDB
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "cryptoconnect")
    
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    print("🔍 Debugging User Holdings Issue")
    print("=" * 50)
    
    # Find the user by email from the logs
    user_email = "jainishjpatel1808@gmail.com"
    user = await db.users.find_one({"email": user_email})
    
    if not user:
        print(f"❌ User not found with email: {user_email}")
        return
    
    user_id = str(user["_id"])
    print(f"✅ Found user: {user['username']} (ID: {user_id})")
    print(f"   Email: {user['email']}")
    print(f"   User Type: {user.get('userType', 'N/A')}")
    
    # Check all transactions for this user
    print(f"\n🔍 Looking for transactions with user_id: {user_id}")
    
    transactions = await db.transactions.find({"user_id": user_id}).to_list(None)
    print(f"📊 Found {len(transactions)} transactions for user_id: {user_id}")
    
    if len(transactions) == 0:
        # Try with ObjectId format
        try:
            user_object_id = ObjectId(user_id)
            transactions_obj = await db.transactions.find({"user_id": user_object_id}).to_list(None)
            print(f"📊 Found {len(transactions_obj)} transactions for user_id as ObjectId")
        except:
            print("❌ Could not convert user_id to ObjectId")
    
    # Check all transactions in the database to see what user_ids exist
    print(f"\n🔍 Checking all transactions in database...")
    all_transactions = await db.transactions.find({}).to_list(None)
    print(f"📊 Total transactions in database: {len(all_transactions)}")
    
    # Group by user_id to see what formats exist
    user_id_formats = {}
    for tx in all_transactions:
        tx_user_id = tx.get("user_id")
        if tx_user_id not in user_id_formats:
            user_id_formats[tx_user_id] = 0
        user_id_formats[tx_user_id] += 1
    
    print(f"\n📋 User ID formats found in transactions:")
    for uid, count in user_id_formats.items():
        print(f"   {uid} ({type(uid).__name__}): {count} transactions")
        if uid == user_id:
            print(f"      ✅ MATCHES our user!")
    
    # Show the specific transaction from your logs
    print(f"\n🔍 Looking for the specific transaction from your logs...")
    specific_tx = await db.transactions.find_one({
        "property_id": "68ce70f2ca6f1a985cc1f469",
        "amount": 20,
        "tokens": 100
    })
    
    if specific_tx:
        print(f"✅ Found the transaction:")
        print(f"   Transaction ID: {specific_tx['_id']}")
        print(f"   User ID: {specific_tx['user_id']} ({type(specific_tx['user_id']).__name__})")
        print(f"   Property ID: {specific_tx['property_id']}")
        print(f"   Status: {specific_tx['status']}")
        print(f"   Type: {specific_tx['transaction_type']}")
        print(f"   Tokens: {specific_tx['tokens']}")
        print(f"   Amount: {specific_tx['amount']}")
        
        # Check if user_ids match
        if str(specific_tx['user_id']) == user_id:
            print(f"   ✅ User IDs match!")
        else:
            print(f"   ❌ User ID mismatch!")
            print(f"      Transaction user_id: {specific_tx['user_id']}")
            print(f"      Current user_id: {user_id}")
    else:
        print(f"❌ Could not find the specific transaction")
    
    # Check the property
    property_id = "68ce70f2ca6f1a985cc1f469"
    property_obj = await db.properties.find_one({"_id": ObjectId(property_id)})
    if property_obj:
        print(f"\n✅ Found property: {property_obj['title']}")
        print(f"   Status: {property_obj['status']}")
        print(f"   Token Price: {property_obj['token_price']}")
    else:
        print(f"\n❌ Could not find property with ID: {property_id}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(debug_user_holdings())