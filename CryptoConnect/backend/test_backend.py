#!/usr/bin/env python3
"""
Simple test script to check if the backend is working
"""
import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_backend():
    """Test basic backend functionality"""
    try:
        # Test imports
        print("Testing imports...")
        from app.config import settings
        print(f"✓ Config loaded: MongoDB URL = {settings.mongodb_url}")
        
        from app.models.user import User
        from app.models.property import Property
        from app.models.transaction import Transaction
        print("✓ Models imported successfully")
        
        # Test database connection
        print("Testing database connection...")
        from app.database import connect_to_mongo
        await connect_to_mongo()
        print("✓ Database connected successfully")
        
        # Test creating a simple property
        print("Testing property creation...")
        test_property = Property(
            title="Test Property",
            description="Test Description",
            address="Test Address",
            city="Test City",
            country="Test Country",
            property_type="apartment",
            total_value=1000000.0,
            size_sqm=100.0,
            seller_id="test_seller",
            seller_name="Test Seller",
            seller_email="test@example.com"
        )
        
        test_property.calculate_tokens_and_price()
        await test_property.save()
        print(f"✓ Property created with ID: {test_property.id}")
        
        # Clean up
        await test_property.delete()
        print("✓ Test property cleaned up")
        
        print("\n🎉 All tests passed! Backend is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_backend())
    sys.exit(0 if success else 1)