#!/usr/bin/env python3
"""
Create test users for investment testing
"""
import asyncio
import sys
import os
from datetime import datetime

# Add the backend directory to Python path
sys.path.append(os.path.dirname(__file__))

from app.database import connect_to_mongo, close_mongo_connection
from app.models.user import User, UserRole
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

XRP_WALLET = {
    "address": "rGghB5Kp9YEQhZbxg7Pxm3FGd6gZsytQS8",
    "secret": "sEd7t6iGCmeYpBMW4yQxzK8FnJNpsrh"
}

async def create_test_investor():
    """Create a test investor user"""
    print("🔧 Creating test investor user...")
    
    # Check if user already exists
    existing_user = await User.find_one({"email": "investor@test.com"})
    if existing_user:
        print("✅ Test investor already exists")
        return existing_user
    
    # Hash password
    hashed_password = pwd_context.hash("testpass123")
    
    # Create user
    user_data = {
        "username": "testinvestor",
        "email": "investor@test.com", 
        "hashed_password": hashed_password,
        "role": UserRole.INVESTOR,
        "xrpl_wallet_address": XRP_WALLET["address"],
        "xrpl_wallet_seed": XRP_WALLET["secret"],  # Note: should be xrpl_wallet_seed not xrpl_wallet_secret
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    user = User(**user_data)
    await user.insert()
    
    print(f"✅ Created test investor: {user.username} ({user.email})")
    print(f"   📧 Email: {user.email}")
    print(f"   🔑 Password: testpass123")
    print(f"   👤 Role: {user.role.value}")
    print(f"   💰 Wallet: {user.xrpl_wallet_address}")
    
    return user

async def main():
    """Main function"""
    print("🚀 Creating Test User for Investment Testing")
    print("=" * 60)
    
    try:
        # Connect to database
        await connect_to_mongo()
        
        # Create test investor
        investor = await create_test_investor()
        
        print("\n" + "=" * 60)
        print("✅ Test user creation completed!")
        print("\n💡 You can now login with:")
        print("   📧 Email: investor@test.com")
        print("   🔑 Password: testpass123")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(main())