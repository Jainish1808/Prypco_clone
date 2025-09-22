"""
Create a test property for investment testing
"""
import asyncio
from app.models.property import Property, PropertyStatus
from app.database import connect_to_mongo
from bson import ObjectId

async def create_test_property():
    await connect_to_mongo()
    
    # Create a test property for investment
    test_property = Property(
        title="Test Investment Property",
        description="A beautiful property available for tokenized investment",
        address="123 Investment Street",
        city="Investment City", 
        country="USA",
        property_type="apartment",  # Use valid enum value
        total_value=100000.0,
        size_sqm=150.0,
        total_tokens=1000,
        token_price=0.2,  # $0.20 per token
        tokens_sold=0,
        expected_rental_yield=0.08,
        status=PropertyStatus.APPROVED,  # Set as approved so it's available for investment
        seller_id="68cbf0515263fa27a42ee61e",  # Your user ID
        seller_name="Test Seller",  # Required field
        seller_email="seller@test.com",  # Required field
        xrpl_token_created=True,  # Mark as tokenized
        token_symbol="TST",
        xrpl_issuer_address="rDummyIssuerAddress123",
        images=[],
        documents=[]
    )
    
    await test_property.save()
    print(f"✅ Created test property: {test_property.title} (ID: {test_property.id})")
    print(f"   💰 Total value: ${test_property.total_value}")
    print(f"   🪙 Token price: ${test_property.token_price}")
    print(f"   📊 Total tokens: {test_property.total_tokens}")
    print(f"   🟢 Status: {test_property.status}")

if __name__ == "__main__":
    asyncio.run(create_test_property())