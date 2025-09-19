from beanie import Document
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    INVESTOR = "investor"
    SELLER = "seller"
    ADMIN = "admin"


class KYCStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class User(Document):
    email: EmailStr
    username: str
    hashed_password: str
    role: UserRole = UserRole.INVESTOR
    is_active: bool = True
    is_kyc_verified: bool = False
    kyc_status: KYCStatus = KYCStatus.PENDING
    
    # Profile information
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    
    # XRPL wallet information
    xrpl_wallet_address: Optional[str] = None
    xrpl_wallet_seed: Optional[str] = None  # Encrypted in production
    
    # KYC data
    kyc_data: Optional[Dict[str, Any]] = None
    
    # Timestamps
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    
    class Settings:
        collection = "users"
        indexes = [
            "email",
            "username",
            "xrpl_wallet_address"
        ]


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    userType: str = "investor"  # Maps to role
    
    # For backward compatibility
    role: Optional[UserRole] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserLogin(BaseModel):
    username: str  # Frontend sends username, not email
    password: str
    
    # For backward compatibility
    email: Optional[EmailStr] = None


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    username: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    walletAddress: Optional[str] = None
    isKYCVerified: bool = False
    userType: str = "investor"  # Maps to role
    createdAt: datetime
    
    # Additional fields for compatibility
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    kyc_status: Optional[KYCStatus] = None
    phone: Optional[str] = None


class KYCSubmission(BaseModel):
    first_name: str
    last_name: str
    phone: str
    address: str
    date_of_birth: str
    document_type: str
    document_number: str