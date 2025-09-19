#!/usr/bin/env python3
"""
Test property submission endpoint
"""
import asyncio
import sys
import os
import json

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_property_submission():
    """Test property submission functionality"""
    try:
        print("Testing property submission...")
        
        # Import required modules
        from app.database import connect_to_mongo
        from app.models.property import Property, PropertyCreate
        from app.models.user import User, UserRole
        from app.routers.seller import submit_property, PropertyCreateWithImages
        
        # Connect to database
        await connect_to_mongo()
        print("✓ Database connected")
        
        # Create a test user
        test_user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
            role=UserRole.SELLER,
            first_name="Test",
            last_name="User"
        )
        await test_user.save()
        print(f"✓ Test user created: {test_user.id}")
        
        # Create test property data
        property_data = PropertyCreateWithImages(
            title="Test Property Submission",
            description="This is a test property",
            address="123 Test Street",
            city="Test City",
            country="Test Country",
            property_type="apartment",
            total_value=2000000.0,
            size_sqm=150.0,
            bedrooms=3,
            bathrooms=2,
            parking_spaces=1,
            year_built=2020,
            monthly_rent=8000.0,
            images=[]
        )
        
        # Test property submission
        result = await submit_property(property_data, test_user)
        print(f"✓ Property submitted successfully: {result.id}")
        print(f"  Title: {result.title}")
        print(f"  Total Tokens: {result.total_tokens}")
        print(f"  Token Price: {result.token_price}")
        print(f"  Status: {result.status}")
        
        # Clean up
        property_obj = await Property.get(result.id)
        if property_obj:
            await property_obj.delete()
        await test_user.delete()
        print("✓ Test data cleaned up")
        
        print("\n🎉 Property submission test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_property_submission())
    sys.exit(0 if success else 1)