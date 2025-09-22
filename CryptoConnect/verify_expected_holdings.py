#!/usr/bin/env python3
"""
Quick script to verify the expected holdings based on your MongoDB transaction
"""

# Your transaction data from MongoDB
transaction = {
    "user_id": "68cbf0515263fa27a42ee61e",
    "transaction_type": "token_purchase", 
    "status": "completed",
    "tokens": 100,
    "amount": 20,
    "token_price": 0.2,
    "property_id": "68ce70f2ca6f1a985cc1f469",
    "metadata": {
        "investment_amount_xrp": 211.392,
        "property_title": "Alex"
    }
}

print("=== EXPECTED PORTFOLIO CALCULATION ===")
print(f"Property: {transaction['metadata']['property_title']}")
print(f"Tokens purchased: {transaction['tokens']}")
print(f"Amount invested: AED {transaction['amount']}")
print(f"Token price: AED {transaction['token_price']}")
print(f"XRP invested: {transaction['metadata']['investment_amount_xrp']}")

print("\n=== WHAT SHOULD APPEAR IN YOUR PORTFOLIO ===")
print("📊 Portfolio Holdings:")
print(f"  - Property: Alex")
print(f"  - Tokens owned: 100")
print(f"  - Total investment: AED 20.00") 
print(f"  - Current value: AED {100 * transaction['token_price']}")
print(f"  - Property status: (depends on property document)")

print("\n=== DEBUGGING CHECKLIST ===")
print("✅ Transaction exists in MongoDB")
print("✅ Transaction is 'completed' status")
print("✅ Transaction type is 'token_purchase'")  
print("✅ User ID format is valid ObjectId string")
print("✅ Backend code fixed to use proper queries")

print("\n=== IF STILL NOT WORKING ===")
print("Check the backend console logs when you:")
print("1. Login to the frontend")
print("2. Navigate to 'My Portfolio'")
print("3. Look for debug messages starting with 🔍 and 📊")
print("4. The logs will show exactly what's being queried and found")

print("\n=== BACKEND LOG EXPECTATIONS ===")
print("You should see:")
print("🔍 Getting holdings for user: [your_username] (ID: 68cbf0515263fa27a42ee61e)")
print("📊 Found 1 completed purchase transactions")  
print("  - token_purchase: 100 tokens, Property: 68ce70f2ca6f1a985cc1f469")
print("📋 Returning 1 holdings to frontend")