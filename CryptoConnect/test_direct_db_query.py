#!/usr/bin/env python3
"""
Direct database test to debug why holdings query fails
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

async def test_transaction_queries():
    from app.database import init_db
    from app.models.transaction import Transaction, TransactionType, TransactionStatus
    from app.models.user import User
    
    # Initialize database connection
    await init_db()
    
    # Your user ID from the transaction
    user_id = "68cbf0515263fa27a42ee61e"
    
    print("=== DIRECT DATABASE QUERY TEST ===")
    print(f"Testing queries for user_id: {user_id}")
    
    # Test 1: Find all transactions for this user
    all_transactions = await Transaction.find(
        Transaction.user_id == user_id
    ).to_list()
    
    print(f"\n📊 Found {len(all_transactions)} total transactions:")
    for tx in all_transactions:
        print(f"  - ID: {tx.id}")
        print(f"    Type: {tx.transaction_type} (Python type: {type(tx.transaction_type)})")
        print(f"    Status: {tx.status} (Python type: {type(tx.status)})")
        print(f"    Tokens: {tx.tokens}")
        print(f"    Property: {tx.property_id}")
        print()
    
    # Test 2: Try enum-based query
    print("Testing ENUM-based query...")
    enum_transactions = await Transaction.find(
        Transaction.user_id == user_id,
        Transaction.transaction_type.in_([TransactionType.TOKEN_PURCHASE, TransactionType.SECONDARY_MARKET_BUY]),
        Transaction.status == TransactionStatus.COMPLETED
    ).to_list()
    
    print(f"📊 ENUM query found {len(enum_transactions)} transactions")
    
    # Test 3: Try string-based query  
    print("Testing STRING-based query...")
    string_transactions = await Transaction.find(
        Transaction.user_id == user_id,
        Transaction.transaction_type.in_(["token_purchase", "secondary_market_buy"]),
        Transaction.status == "completed"
    ).to_list()
    
    print(f"📊 STRING query found {len(string_transactions)} transactions")
    
    # Test 4: Check enum values
    print(f"\n🔍 Enum values:")
    print(f"TransactionType.TOKEN_PURCHASE = {TransactionType.TOKEN_PURCHASE}")
    print(f"TransactionStatus.COMPLETED = {TransactionStatus.COMPLETED}")
    
    # Test 5: Check if user exists
    try:
        from bson import ObjectId
        user = await User.get(ObjectId(user_id))
        if user:
            print(f"\n✅ User found: {user.username} ({user.email})")
        else:
            print(f"\n❌ User not found with ID: {user_id}")
    except Exception as e:
        print(f"\n❌ Error finding user: {e}")

if __name__ == "__main__":
    asyncio.run(test_transaction_queries())