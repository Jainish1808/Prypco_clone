#!/usr/bin/env python3
"""
Debug script to verify user ID matching between JWT auth and MongoDB queries
"""

# The user_id from your MongoDB transaction
mongo_user_id = "68cbf0515263fa27a42ee61e"

print("=== USER ID DEBUG ===")
print(f"MongoDB Transaction user_id: {mongo_user_id}")
print(f"Type: {type(mongo_user_id)}")
print(f"Length: {len(mongo_user_id)}")

# Check if it's a valid ObjectId format
try:
    from bson import ObjectId
    
    # Test if it's a valid ObjectId string
    if ObjectId.is_valid(mongo_user_id):
        print(f"✅ Valid ObjectId string")
        
        # Convert to ObjectId and back to string
        obj_id = ObjectId(mongo_user_id)
        print(f"ObjectId object: {obj_id}")
        print(f"ObjectId as string: {str(obj_id)}")
        print(f"Match check: {str(obj_id) == mongo_user_id}")
        
    else:
        print(f"❌ Invalid ObjectId format")
        
except ImportError:
    print("⚠️ bson not available, but that's okay for this test")

print("\n=== TRANSACTION QUERY DEBUG ===")
print("Your transaction shows:")
print("- user_id: '68cbf0515263fa27a42ee61e'")
print("- transaction_type: 'token_purchase'")
print("- status: 'completed'")
print("- tokens: 100")
print("- property_id: '68ce70f2ca6f1a985cc1f469'")

print("\n=== EXPECTED BACKEND BEHAVIOR ===")
print("1. User logs in → JWT contains user_id")
print("2. Holdings endpoint gets current_user.id") 
print("3. Converts to string: str(current_user.id)")
print("4. Queries: Transaction.user_id == user_id_string")
print("5. Should find your transaction!")

print("\n=== DEBUGGING SUMMARY ===")
print("✅ Fixed holdings endpoint to use proper user_id string conversion")
print("✅ Fixed transaction queries to use enum types instead of string literals")
print("✅ Added comprehensive debugging logs")
print("✅ Fixed income statements endpoint")
print("✅ Fixed secondary market token balance calculation")
print()
print("Next step: Restart backend and check portfolio!")