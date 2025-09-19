#!/usr/bin/env python3
"""
Test full API flow including authentication
"""
import asyncio
import sys
import os
import json
from datetime import timedelta

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_full_api():
    """Test full API flow"""
    try:
        print("Testing full API flow...")
        
        # Import required modules
        from app.database import connect_to_mongo
        from app.models.user import User, UserRole, UserCreate
        from app.models.property import Property
        from app.routers.auth import register_user, login_user
        from app.routers.seller import submit_property, PropertyCreateWithImages
        from app.auth import create_access_token, get_current_active_user
        from app.config import settings
        
        # Connect to database
        await connect_to_mongo()
        print("✓ Database connected")
        
        # Test user registration
        user_data = UserCreate(
            email="testapi@example.com",
            username="testapi",
            password="testpassword123",
            firstName="Test",
            lastName="API",
            userType="seller"
        )
        
        registered_user = await register_user(user_data)
        print(f"✓ User registered: {registered_user.id}")
        
        # Test user login
        from app.models.user import UserLogin
        login_data = UserLogin(
            username="testapi",
            password="testpassword123"
        )
        
        login_result = await login_user(login_data)
        print(f"✓ User logged in, token: {login_result['access_token'][:20]}...")
        
        # Get the user object for property submission
        user = await User.find_one(User.username == "testapi")
        
        # Test property submission with authenticated user
        property_data = PropertyCreateWithImages(
            title="API Test Property",
            description="This is a test property via API",
            address="456 API Street",
            city="API City",
            country="API Country",
            property_type="apartment",
            total_value=1500000.0,
            size_sqm=120.0,
            bedrooms=2,
            bathrooms=2,
            parking_spaces=1,
            year_built=2021,
            monthly_rent=6000.0,
            images=[]
        )
        
        result = await submit_property(property_data, user)
        print(f"✓ Property submitted via API: {result.id}")
        print(f"  Title: {result.title}")
        print(f"  Seller: {result.seller_name}")
        print(f"  Status: {result.status}")
        
        # Test getting seller properties
        from app.routers.seller import get_seller_properties
        properties = await get_seller_properties(user)
        print(f"✓ Retrieved {len(properties)} properties for seller")
        
        # Clean up
        property_obj = await Property.get(result.id)
        if property_obj:
            await property_obj.delete()
        await user.delete()
        print("✓ Test data cleaned up")
        
        print("\n🎉 Full API test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_full_api())
    sys.exit(0 if success else 1)