"""
Data migration script to fix existing properties in the database.
This script updates properties with invalid seller IDs to associate them with actual users.
"""

import asyncio
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.models.property import Property, PropertyStatus
from app.models.user import User
from app.config import settings


async def migrate_properties():
    """Fix properties with invalid seller IDs"""
    # Initialize database connection
    client = AsyncIOMotorClient(settings.mongodb_url)
    database = client[settings.database_name]
    
    await init_beanie(database=database, document_models=[User, Property])
    
    print("🔧 Starting property migration...")
    
    # Get all properties
    all_properties = await Property.find().to_list()
    print(f"Found {len(all_properties)} properties in database")
    
    # Get test seller user
    seller_user = await User.find_one(User.email == "seller@cryptoconnect.com")
    if not seller_user:
        print("❌ Test seller not found, cannot migrate properties")
        return
    
    print(f"✅ Found test seller: {seller_user.email}")
    
    # Update properties with invalid seller_ids
    updated_count = 0
    for prop in all_properties:
        # Check if seller_id is not a valid ObjectId format or doesn't exist as a user
        try:
            if prop.seller_id == "sample_seller" or len(prop.seller_id) < 24:
                # Invalid seller_id, update to test seller
                prop.seller_id = str(seller_user.id)
                prop.seller_name = f"{seller_user.first_name} {seller_user.last_name}"
                prop.seller_email = seller_user.email
                await prop.save()
                updated_count += 1
                print(f"✅ Updated property '{prop.title}' to seller: {prop.seller_name}")
        except Exception as e:
            print(f"❌ Error updating property {prop.title}: {e}")
    
    print(f"🎉 Migration complete! Updated {updated_count} properties")
    
    # Verify the migration
    print("\n📊 Verification:")
    properties_by_seller = await Property.find(Property.seller_id == str(seller_user.id)).to_list()
    print(f"Properties now owned by test seller: {len(properties_by_seller)}")
    
    for prop in properties_by_seller:
        print(f"  - {prop.title} (Status: {prop.status}, ID: {prop.id})")


if __name__ == "__main__":
    asyncio.run(migrate_properties())