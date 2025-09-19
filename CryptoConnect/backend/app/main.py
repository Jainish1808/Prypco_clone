from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi import Depends
from app.database import connect_to_mongo, close_mongo_connection
from app.routers import auth, properties, seller, investor, admin, upload, market
from app.config import settings
from app.auth import get_current_active_user
from app.models.user import User


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()


app = FastAPI(
    title="CryptoConnect API",
    description="Tokenized Real Estate Investment Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(properties.router)
app.include_router(seller.router)
app.include_router(investor.router)
app.include_router(admin.router)
app.include_router(upload.router)
app.include_router(market.router)


@app.get("/")
async def root():
    return {"message": "CryptoConnect API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "CryptoConnect API is running"}


@app.get("/api/health")
async def api_health_check():
    return {"status": "healthy", "message": "CryptoConnect API is running", "timestamp": "2024-01-01T00:00:00Z"}


@app.get("/debug/state")
async def debug_state():
    """Debug endpoint to check system state"""
    from app.models.user import User
    from app.models.property import Property
    from app.models.transaction import Transaction
    
    try:
        user_count = await User.find().count()
        property_count = await Property.find().count()
        transaction_count = await Transaction.find().count()
        
        # Get sample data
        sample_users = await User.find().limit(3).to_list()
        sample_properties = await Property.find().limit(3).to_list()
        
        return {
            "status": "healthy",
            "database": "connected",
            "counts": {
                "users": user_count,
                "properties": property_count,
                "transactions": transaction_count
            },
            "sample_data": {
                "users": [{"id": str(u.id), "email": u.email, "role": str(u.role), "is_kyc_verified": u.is_kyc_verified} for u in sample_users],
                "properties": [{"id": str(p.id), "title": p.title, "status": p.status} for p in sample_properties]
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "disconnected",
            "error": str(e)
        }


@app.get("/debug/auth")
async def debug_auth(request):
    """Debug endpoint to check authentication headers"""
    headers = dict(request.headers)
    return {
        "headers": headers,
        "authorization": headers.get("authorization", "No auth header"),
        "user_agent": headers.get("user-agent", "No user agent")
    }


@app.post("/debug/test-property")
async def test_property_submission(data: dict):
    """Test endpoint for property submission"""
    return {
        "message": "Property data received",
        "data": data,
        "status": "success"
    }


@app.post("/api/seller/property/submit-debug")
async def debug_property_submission(data: dict):
    """Debug endpoint for property submission without auth"""
    try:
        from app.models.property import Property
        
        # Create a simple property for testing
        property_obj = Property(
            title=data.get("title", "Test Property"),
            description=data.get("description", "Test Description"),
            address=data.get("address", "Test Address"),
            city=data.get("city", "Test City"),
            country=data.get("country", "Test Country"),
            property_type=data.get("property_type", "apartment"),
            total_value=float(data.get("total_value", 1000000)),
            size_sqm=float(data.get("size_sqm", 100)),
            seller_id="debug_seller",
            seller_name="Debug Seller",
            seller_email="debug@test.com"
        )
        
        # Calculate tokens and price
        property_obj.calculate_tokens_and_price()
        
        # Save to database
        await property_obj.save()
        
        return {
            "message": "Debug property created successfully",
            "property_id": str(property_obj.id),
            "data": data
        }
    except Exception as e:
        return {
            "message": "Error creating debug property",
            "error": str(e),
            "data": data
        }


@app.get("/api/auth-test")
async def test_auth(current_user: User = Depends(get_current_active_user)):
    """Test endpoint to verify authentication is working"""
    return {
        "message": "Authentication successful",
        "user_id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role.value,
        "is_active": current_user.is_active
    }


@app.get("/api/debug/properties")
async def debug_properties():
    """Debug endpoint to check all properties in database"""
    try:
        from app.models.property import Property
        properties = await Property.find().to_list()
        
        return {
            "total_properties": len(properties),
            "properties": [
                {
                    "id": str(prop.id),
                    "title": prop.title,
                    "seller_id": prop.seller_id,
                    "seller_name": prop.seller_name,
                    "status": prop.status,
                    "created_at": prop.created_at.isoformat()
                }
                for prop in properties
            ]
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/debug/user-properties/{user_id}")
async def debug_user_properties(user_id: str):
    """Debug endpoint to check properties for a specific user"""
    try:
        from app.models.property import Property
        properties = await Property.find(Property.seller_id == user_id).to_list()
        
        return {
            "user_id": user_id,
            "total_properties": len(properties),
            "properties": [
                {
                    "id": str(prop.id),
                    "title": prop.title,
                    "seller_id": prop.seller_id,
                    "seller_name": prop.seller_name,
                    "status": prop.status,
                    "created_at": prop.created_at.isoformat()
                }
                for prop in properties
            ]
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )