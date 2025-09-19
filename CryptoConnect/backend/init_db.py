#!/usr/bin/env python3
"""
Database Initialization Script for CryptoConnect
This script initializes the MongoDB database and creates sample data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
from app.database import connect_to_mongo, close_mongo_connection
from app.models.user import User, UserRole
from app.models.property import Property, PropertyType, PropertyStatus
from app.auth import get_password_hash

async def create_admin_user():
    """Create a default admin user"""
    admin_email = "admin@cryptoconnect.com"
    
    # Check if admin already exists
    existing_admin = await User.find_one(User.email == admin_email)
    if existing_admin:
        print(f"✅ Admin user already exists: {admin_email}")
        return existing_admin
    
    # Create admin user
    admin_user = User(
        email=admin_email,
        username="admin",
        hashed_password=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        first_name="Admin",
        last_name="User",
        is_kyc_verified=True,
        kyc_status="verified"
    )
    
    await admin_user.save()
    print(f"✅ Created admin user: {admin_email} (password: admin123)")
    return admin_user

async def create_test_seller():
    """Create a test seller user"""
    seller_email = "seller@cryptoconnect.com"
    
    # Check if seller already exists
    existing_seller = await User.find_one(User.email == seller_email)
    if existing_seller:
        print(f"✅ Test seller already exists: {seller_email}")
        return existing_seller
    
    # Create seller user
    seller_user = User(
        email=seller_email,
        username="seller",
        hashed_password=get_password_hash("seller123"),
        role=UserRole.SELLER,
        first_name="Test",
        last_name="Seller",
        is_kyc_verified=True,
        kyc_status="verified"
    )
    
    await seller_user.save()
    print(f"✅ Created test seller: {seller_email} (password: seller123)")
    return seller_user

async def create_sample_property():
    """Create a sample property for testing"""
    # Get the test seller first
    seller_user = await User.find_one(User.email == "seller@cryptoconnect.com")
    if not seller_user:
        print("❌ Test seller not found, cannot create proper sample property")
        return None
    
    seller_id = str(seller_user.id)
    seller_name = f"{seller_user.first_name} {seller_user.last_name}"
    seller_email = seller_user.email
    
    # Check if sample property already exists
    existing_property = await Property.find_one(Property.title == "Luxury Dubai Marina Apartment")
    if existing_property:
        # Update existing property if it has invalid seller_id
        if existing_property.seller_id == "sample_seller":
            existing_property.seller_id = seller_id
            existing_property.seller_name = seller_name
            existing_property.seller_email = seller_email
            await existing_property.save()
            print(f"✅ Updated existing property seller to: {seller_name}")
        else:
            print("✅ Sample property already exists with correct seller")
        return existing_property
    
    # Create sample property
    sample_property = Property(
        title="Luxury Dubai Marina Apartment",
        description="A stunning 2-bedroom apartment in the heart of Dubai Marina with breathtaking views of the marina and city skyline. This premium property offers modern amenities and is perfect for both living and investment.",
        address="Dubai Marina, Dubai",
        city="Dubai",
        country="UAE",
        property_type=PropertyType.APARTMENT,
        total_value=2600000.0,  # AED 2.6M
        size_sqm=130.0,  # 130 sqm
        total_tokens=1300000,  # 130 * 10,000
        token_price=2.0,  # 2,600,000 / 1,300,000
        bedrooms=2,
        bathrooms=2,
        parking_spaces=1,
        year_built=2020,
        monthly_rent=12000.0,  # AED 12,000/month
        seller_id=seller_id,
        seller_name=seller_name,
        seller_email=seller_email,
        status=PropertyStatus.APPROVED
    )
    
    # Calculate annual yield
    annual_rent = sample_property.monthly_rent * 12
    sample_property.annual_yield = (annual_rent / sample_property.total_value) * 100
    
    await sample_property.save()
    print(f"✅ Created sample property: {sample_property.title}")
    print(f"   Total Tokens: {sample_property.total_tokens:,}")
    print(f"   Token Price: AED {sample_property.token_price:.4f}")
    print(f"   Annual Yield: {sample_property.annual_yield:.2f}%")
    
    return sample_property

async def fix_existing_properties():
    """Fix any existing properties with invalid seller IDs"""
    print("🔧 Checking for properties with invalid seller IDs...")
    
    # Get the test seller
    seller_user = await User.find_one(User.email == "seller@cryptoconnect.com")
    if not seller_user:
        print("❌ Test seller not found, cannot fix properties")
        return
    
    # Find properties with invalid seller_ids
    invalid_properties = await Property.find(Property.seller_id == "sample_seller").to_list()
    
    if not invalid_properties:
        print("✅ No properties with invalid seller IDs found")
        return
    
    print(f"🔧 Found {len(invalid_properties)} properties to fix...")
    
    for prop in invalid_properties:
        prop.seller_id = str(seller_user.id)
        prop.seller_name = f"{seller_user.first_name} {seller_user.last_name}"
        prop.seller_email = seller_user.email
        await prop.save()
        print(f"✅ Fixed property: {prop.title}")
    
    print(f"🎉 Fixed {len(invalid_properties)} properties!")

async def init_database():
    """Initialize the database with sample data"""
    print("🚀 Initializing CryptoConnect Database")
    print("=" * 40)
    
    try:
        # Connect to database
        await connect_to_mongo()
        print("✅ Connected to MongoDB")
        
        # Create admin user
        await create_admin_user()
        
        # Create test seller
        await create_test_seller()
        
        # Fix any existing properties with invalid seller IDs
        await fix_existing_properties()
        
        # Create sample property
        await create_sample_property()
        
        print("\n🎉 Database initialization completed!")
        print("\nYou can now:")
        print("1. Login as admin: admin@cryptoconnect.com / admin123")
        print("2. Register as investor or seller")
        print("3. Browse the sample property")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(init_database())