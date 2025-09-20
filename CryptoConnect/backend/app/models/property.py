from beanie import Document
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PropertyStatus(str, Enum):
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    TOKENIZED = "tokenized"
    SOLD_OUT = "sold_out"


class PropertyType(str, Enum):
    APARTMENT = "apartment"
    VILLA = "villa"
    OFFICE = "office"
    RETAIL = "retail"
    WAREHOUSE = "warehouse"


class Property(Document):
    # Basic property information
    title: str
    description: str
    address: str
    city: str
    country: str
    property_type: PropertyType
    
    # Financial details
    total_value: float  # Property value in AED
    size_sqm: float  # Size in square meters
    
    # Tokenization details
    total_tokens: int = 0  # Calculated as size_sqm * 10,000
    token_price: float = 0.0  # Calculated as total_value / total_tokens
    tokens_sold: int = 0
    token_symbol: Optional[str] = None  # XRPL token symbol
    
    # Property details
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    parking_spaces: Optional[int] = None
    year_built: Optional[int] = None
    
    # Rental information
    monthly_rent: Optional[float] = None
    annual_yield: Optional[float] = None
    
    # Seller information
    seller_id: str  # Reference to User document
    seller_name: str
    seller_email: str
    
    # Status and approval
    status: PropertyStatus = PropertyStatus.PENDING_REVIEW
    admin_notes: Optional[str] = None
    
    # Documents and media
    images: List[str] = []  # URLs to property images
    documents: List[Dict[str, str]] = []  # Legal documents
    
    # XRPL integration
    xrpl_token_created: bool = False
    xrpl_issuer_address: Optional[str] = None
    xrpl_creation_tx_hash: Optional[str] = None
    xrpl_explorer_url: Optional[str] = None  # Link to testnet explorer
    token_holders: List[Dict[str, Any]] = []  # List of current token holders
    
    # Timestamps
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    approved_at: Optional[datetime] = None
    
    class Settings:
        collection = "properties"
        indexes = [
            "seller_id",
            "status",
            "property_type",
            "city"
        ]
    
    def calculate_tokens_and_price(self):
        """Calculate total tokens and token price based on formulas"""
        self.total_tokens = int(self.size_sqm * 10000)
        self.token_price = self.total_value / self.total_tokens if self.total_tokens > 0 else 0


class PropertyCreate(BaseModel):
    title: str
    description: str
    address: str
    city: str
    country: str
    property_type: PropertyType
    total_value: float
    size_sqm: float
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    parking_spaces: Optional[int] = None
    year_built: Optional[int] = None
    monthly_rent: Optional[float] = None


class PropertyResponse(BaseModel):
    id: str
    title: str
    description: str
    address: str
    city: str
    country: str
    property_type: PropertyType
    total_value: float
    size_sqm: float
    total_tokens: int
    token_price: float
    tokens_sold: int
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    parking_spaces: Optional[int] = None
    year_built: Optional[int] = None
    monthly_rent: Optional[float] = None
    annual_yield: Optional[float] = None
    seller_name: str
    status: PropertyStatus
    images: List[str] = []
    created_at: datetime


class PropertyUpdateAdmin(BaseModel):
    """Admin-only property updates"""
    status: Optional[PropertyStatus] = None
    admin_notes: Optional[str] = None


class PropertyUpdateSeller(BaseModel):
    """Seller property updates (only allowed for pending review properties)"""
    title: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    property_type: Optional[PropertyType] = None
    total_value: Optional[float] = None
    size_sqm: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    parking_spaces: Optional[int] = None
    year_built: Optional[int] = None
    monthly_rent: Optional[float] = None
    images: Optional[List[str]] = None


class InvestmentRequest(BaseModel):
    property_id: str
    investment_amount: float  # Amount in AED
    tokens_to_purchase: int