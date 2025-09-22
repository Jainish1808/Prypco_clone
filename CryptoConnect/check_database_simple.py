#!/usr/bin/env python3

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def check_database():
    """Simple database check to see what data exists"""
    
    # Connect to MongoDB
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "cryptoconnect")
    
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    print("🔍 Checking CryptoConnect Database")
    print("=" * 50)
    
    # Check users
    users = await db.users.find({}).to_list(None)
    print(f"👥 Users: {len(users)}")
    for user in users:
        print(f"   - {user.get('username', 'N/A')} ({user.get('email', 'N/A')}) - Type: {user.get('userType', 'N/A')}")
    
    # Check properties
    properties = await db.properties.find({}).to_list(None)
    print(f"\n🏠 Properties: {len(properties)}")
    for prop in properties:
        print(f"   - {prop.get('title', 'N/A')} - Status: {prop.get('status', 'N/A')} - Tokens: {prop.get('total_tokens', 0)}")
    
    # Check transactions
    transactions = await db.transactions.find({}).to_list(None)
    print(f"\n💰 Transactions: {len(transactions)}")
    
    # Group transactions by user
    user_transactions = {}
    for tx in transactions:
        user_id = tx.get('user_id')
        if user_id not in user_transactions:
            user_transactions[user_id] = []
        user_transactions[user_id].append(tx)
    
    for user_id, txs in user_transactions.items():
        print(f"\n   User {user_id}:")
        for tx in txs:
            print(f"     - {tx.get('transaction_type', 'N/A')} | {tx.get('status', 'N/A')} | {tx.get('tokens', 0)} tokens | ${tx.get('amount', 0)}")
    
    # Check the specific transaction from the logs
    print(f"\n🔍 Looking for the specific transaction...")
    specific_tx = await db.transactions.find_one({
        "property_id": "68ce70f2ca6f1a985cc1f469",
        "amount": 20,
        "tokens": 100
    })
    
    if specific_tx:
        print(f"✅ Found the transaction:")
        print(f"   User ID: {specific_tx['user_id']}")
        print(f"   Property ID: {specific_tx['property_id']}")
        print(f"   Status: {specific_tx['status']}")
        print(f"   Type: {specific_tx['transaction_type']}")
        print(f"   Tokens: {specific_tx['tokens']}")
        print(f"   Amount: ${specific_tx['amount']}")
        
        # Find the user for this transaction
        user = await db.users.find_one({"_id": ObjectId(specific_tx['user_id'])})
        if user:
            print(f"   User: {user.get('username', 'N/A')} ({user.get('email', 'N/A')})")
        else:
            print(f"   ❌ User not found for ID: {specific_tx['user_id']}")
    else:
        print(f"❌ Specific transaction not found")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_database())