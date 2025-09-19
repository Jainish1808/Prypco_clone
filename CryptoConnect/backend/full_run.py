#!/usr/bin/env python3
"""
Full CryptoConnect FastAPI Backend with Database Integration
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import motor.motor_asyncio
from bson import ObjectId
import asyncio

# Configuration
MONGODB_URL = "mongodb://localhost:27017/cryptoconnect"
JWT_SECRET_KEY = "cryptoconnect-super-secret-jwt-key-change-this-in-production-2024"
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# MongoDB client
client = None
db = None

# Pydantic models
class UserCreate(BaseModel):
    email: str
    username: str
    password: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    userType: str = "investor"

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    walletAddress: Optional[str] = None
    isKYCVerified: bool = False
    userType: str = "investor"
    createdAt: datetime

class PropertyResponse(BaseModel):
    id: str
    name: str
    description: str
    address: str
    propertyType: str
    propertyValue: float
    propertySize: float
    expectedYield: float
    totalTokens: int
    tokenPrice: float
    tokensAvailable: int
    tokensSold: int = 0
    status: str
    images: List[str] = []
    documents: List[dict] = []
    createdAt: datetime

class KYCSubmission(BaseModel):
    firstName: str
    lastName: str
    phone: str
    address: str
    dateOfBirth: str
    documentType: str
    documentNumber: str

# Helper functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise credentials_exception
    
    return user

# FastAPI app
app = FastAPI(title="CryptoConnect API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    global client, db
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
        db = client.cryptoconnect
        
        # Test connection
        await client.admin.command('ping')
        print("✅ Connected to MongoDB")
        
        # Create sample data if needed
        await create_sample_data()
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("   Using in-memory storage for demo")
        db = None

@app.on_event("shutdown")
async def shutdown_db_client():
    if client:
        client.close()

async def create_sample_data():
    """Create sample data if database is empty"""
    if db is None:
        return
    
    # Check if admin user exists
    admin_exists = await db.users.find_one({"email": "admin@cryptoconnect.com"})
    if not admin_exists:
        admin_user = {
            "email": "admin@cryptoconnect.com",
            "username": "admin",
            "hashed_password": get_password_hash("admin123"),
            "firstName": "Admin",
            "lastName": "User",
            "userType": "admin",
            "isKYCVerified": True,
            "createdAt": datetime.utcnow()
        }
        await db.users.insert_one(admin_user)
        print("✅ Created admin user: admin@cryptoconnect.com / admin123")
    
    # Check if sample property exists
    property_exists = await db.properties.find_one({"name": "Luxury Dubai Marina Apartment"})
    if not property_exists:
        sample_property = {
            "name": "Luxury Dubai Marina Apartment",
            "description": "A stunning 2-bedroom apartment in the heart of Dubai Marina with breathtaking views of the marina and city skyline.",
            "address": "Dubai Marina, Dubai, UAE",
            "propertyType": "residential",
            "propertyValue": 2600000.0,
            "propertySize": 130.0,
            "expectedYield": 5.54,
            "totalTokens": 1300000,
            "tokenPrice": 2.0,
            "tokensAvailable": 1300000,
            "tokensSold": 0,
            "status": "approved",
            "images": [],
            "documents": [],
            "createdAt": datetime.utcnow()
        }
        await db.properties.insert_one(sample_property)
        print("✅ Created sample property")

# Routes
@app.get("/")
async def root():
    return {"message": "CryptoConnect API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected" if db else "disconnected"}

@app.post("/api/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    existing_username = await db.users.find_one({"username": user_data.username})
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user_doc = {
        "email": user_data.email,
        "username": user_data.username,
        "hashed_password": hashed_password,
        "firstName": user_data.firstName,
        "lastName": user_data.lastName,
        "userType": user_data.userType,
        "isKYCVerified": False,
        "createdAt": datetime.utcnow()
    }
    
    result = await db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    
    return UserResponse(
        id=str(user_doc["_id"]),
        email=user_doc["email"],
        username=user_doc["username"],
        firstName=user_doc.get("firstName"),
        lastName=user_doc.get("lastName"),
        isKYCVerified=user_doc["isKYCVerified"],
        userType=user_doc["userType"],
        createdAt=user_doc["createdAt"]
    )

@app.post("/api/login")
async def login_user(user_data: UserLogin):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    # Find user
    user = await db.users.find_one({"username": user_data.username})
    if not user or not verify_password(user_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Create token
    access_token_expires = timedelta(minutes=JWT_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["_id"])}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(
            id=str(user["_id"]),
            email=user["email"],
            username=user["username"],
            firstName=user.get("firstName"),
            lastName=user.get("lastName"),
            isKYCVerified=user.get("isKYCVerified", False),
            userType=user.get("userType", "investor"),
            createdAt=user["createdAt"]
        )
    }

@app.get("/api/user", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=str(current_user["_id"]),
        email=current_user["email"],
        username=current_user["username"],
        firstName=current_user.get("firstName"),
        lastName=current_user.get("lastName"),
        isKYCVerified=current_user.get("isKYCVerified", False),
        userType=current_user.get("userType", "investor"),
        createdAt=current_user["createdAt"]
    )

@app.post("/api/logout")
async def logout_user():
    return {"message": "Logged out successfully"}

@app.post("/api/kyc-submit")
async def submit_kyc(kyc_data: KYCSubmission, current_user: dict = Depends(get_current_user)):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    # Update user with KYC data
    await db.users.update_one(
        {"_id": current_user["_id"]},
        {
            "$set": {
                "firstName": kyc_data.firstName,
                "lastName": kyc_data.lastName,
                "phone": kyc_data.phone,
                "isKYCVerified": True,
                "kycData": kyc_data.dict()
            }
        }
    )
    
    return {"message": "KYC submitted successfully", "status": "verified"}

@app.get("/api/properties", response_model=List[PropertyResponse])
async def get_properties():
    if db is None:
        # Return sample data if no database
        return [
            PropertyResponse(
                id="sample-1",
                name="Luxury Dubai Marina Apartment",
                description="A stunning 2-bedroom apartment in the heart of Dubai Marina",
                address="Dubai Marina, Dubai, UAE",
                propertyType="residential",
                propertyValue=2600000.0,
                propertySize=130.0,
                expectedYield=5.54,
                totalTokens=1300000,
                tokenPrice=2.0,
                tokensAvailable=1300000,
                tokensSold=0,
                status="approved",
                images=[],
                documents=[],
                createdAt=datetime.utcnow()
            )
        ]
    
    # Get from database
    properties = []
    async for prop in db.properties.find({"status": "approved"}):
        properties.append(PropertyResponse(
            id=str(prop["_id"]),
            name=prop["name"],
            description=prop["description"],
            address=prop["address"],
            propertyType=prop["propertyType"],
            propertyValue=prop["propertyValue"],
            propertySize=prop["propertySize"],
            expectedYield=prop["expectedYield"],
            totalTokens=prop["totalTokens"],
            tokenPrice=prop["tokenPrice"],
            tokensAvailable=prop["tokensAvailable"],
            tokensSold=prop.get("tokensSold", 0),
            status=prop["status"],
            images=prop.get("images", []),
            documents=prop.get("documents", []),
            createdAt=prop["createdAt"]
        ))
    
    return properties

@app.get("/api/properties/{property_id}", response_model=PropertyResponse)
async def get_property(property_id: str):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        prop = await db.properties.find_one({"_id": ObjectId(property_id)})
        if not prop:
            raise HTTPException(status_code=404, detail="Property not found")
        
        return PropertyResponse(
            id=str(prop["_id"]),
            name=prop["name"],
            description=prop["description"],
            address=prop["address"],
            propertyType=prop["propertyType"],
            propertyValue=prop["propertyValue"],
            propertySize=prop["propertySize"],
            expectedYield=prop["expectedYield"],
            totalTokens=prop["totalTokens"],
            tokenPrice=prop["tokenPrice"],
            tokensAvailable=prop["tokensAvailable"],
            tokensSold=prop.get("tokensSold", 0),
            status=prop["status"],
            images=prop.get("images", []),
            documents=prop.get("documents", []),
            createdAt=prop["createdAt"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid property ID")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("full_run:app", host="0.0.0.0", port=8000, reload=True)