from beanie import Document
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class TransactionType(str, Enum):
    TOKEN_PURCHASE = "token_purchase"
    TOKEN_SALE = "token_sale"
    TOKEN_TRANSFER = "token_transfer"  # New: User to user token transfer
    RENTAL_DISTRIBUTION = "rental_distribution"
    SECONDARY_MARKET_BUY = "secondary_market_buy"
    SECONDARY_MARKET_SELL = "secondary_market_sell"


class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Transaction(Document):
    # Transaction identification
    transaction_type: TransactionType
    status: TransactionStatus = TransactionStatus.PENDING
    
    # User and property references
    user_id: str  # Reference to User document
    property_id: str  # Reference to Property document
    
    # Transaction details
    amount: float  # Amount in AED
    tokens: int  # Number of tokens involved
    token_price: float  # Price per token at time of transaction
    
    # XRPL details
    xrpl_tx_hash: Optional[str] = None
    xrpl_from_address: Optional[str] = None
    xrpl_to_address: Optional[str] = None
    
    # Additional data
    metadata: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    
    # Timestamps
    created_at: datetime = datetime.utcnow()
    completed_at: Optional[datetime] = None
    
    class Settings:
        collection = "transactions"
        indexes = [
            "user_id",
            "property_id",
            "transaction_type",
            "status",
            "xrpl_tx_hash"
        ]


class TransactionResponse(BaseModel):
    id: str
    transaction_type: TransactionType
    status: TransactionStatus
    user_id: str
    property_id: str
    amount: float
    tokens: int
    token_price: float
    xrpl_tx_hash: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class UserHolding(BaseModel):
    property_id: str
    property_title: str
    tokens_owned: int
    total_investment: float
    current_value: float
    ownership_percentage: float
    monthly_rental_income: float


class IncomeStatement(BaseModel):
    property_id: str
    property_title: str
    period: str  # e.g., "2024-01"
    rental_income: float
    your_share: float
    tokens_owned: int
    distribution_date: datetime