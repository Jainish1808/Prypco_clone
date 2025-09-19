"""
Quick database fix script to update properties with invalid seller IDs
"""
import asyncio
import os
import sys

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.models.property import Property
from app.models.user import User
from app.config import settings


async def fix_properties():
    """Fix properties with invalid seller IDs"""
    try:
        # Connect to database
        client = AsyncIOMotorClient(settings.mongodb_url)
        database = client[settings.database_name]
        
        await init_beanie(database=database, document_models=[User, Property])
        
        print("🔧 Fixing property seller associations...")
        
        # Get test seller user
        seller_user = await User.find_one(User.email == "seller@cryptoconnect.com")
        if not seller_user:
            print("❌ Seller user not found!")
            return
            
        print(f"✅ Found seller: {seller_user.first_name} {seller_user.last_name}")
        
        # Find properties with invalid seller_id
        properties_to_fix = await Property.find().to_list()
        
        fixed_count = 0
        for prop in properties_to_fix:
            if prop.seller_id == "sample_seller":
                # Update to use real seller ID
                prop.seller_id = str(seller_user.id)
                prop.seller_name = f"{seller_user.first_name} {seller_user.last_name}"
                prop.seller_email = seller_user.email
                await prop.save()
                fixed_count += 1
                print(f"✅ Fixed property: {prop.title}")
        
        print(f"\n🎉 Fixed {fixed_count} properties!")
        
        # Verify the fix
        seller_properties = await Property.find(Property.seller_id == str(seller_user.id)).to_list()
        print(f"✅ Seller now has {len(seller_properties)} properties")
        
        for prop in seller_properties:
            print(f"  - {prop.title} (Status: {prop.status})")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(fix_properties())