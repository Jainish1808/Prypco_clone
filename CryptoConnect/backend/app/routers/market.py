from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from pydantic import BaseModel
from app.models.user import User
from app.models.property import Property
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.auth import get_current_verified_user
from datetime import datetime
from beanie import Document
from enum import Enum


class OrderType(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderStatus(str, Enum):
    ACTIVE = "active"
    FILLED = "filled"
    CANCELLED = "cancelled"
    PARTIAL = "partial"


class MarketOrder(Document):
    user_id: str
    property_id: str
    order_type: OrderType
    tokens: int
    price_per_token: float
    total_amount: float
    tokens_filled: int = 0
    status: OrderStatus = OrderStatus.ACTIVE
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    expires_at: Optional[datetime] = None
    
    class Settings:
        collection = "market_orders"
        indexes = [
            "user_id",
            "property_id",
            "order_type",
            "status",
            "price_per_token"
        ]


class CreateOrderRequest(BaseModel):
    property_id: str
    order_type: OrderType
    tokens: int
    price_per_token: float


class OrderResponse(BaseModel):
    id: str
    user_id: str
    property_id: str
    property_title: str
    order_type: OrderType
    tokens: int
    price_per_token: float
    total_amount: float
    tokens_filled: int
    tokens_remaining: int
    status: OrderStatus
    created_at: datetime


router = APIRouter(prefix="/api/market", tags=["secondary-market"])


@router.get("/orders")
async def get_market_orders():
    """Get all market orders"""
    # Return empty list for now
    return []


@router.post("/orders")
async def create_market_order(
    order_data: CreateOrderRequest,
    current_user: User = Depends(get_current_verified_user)
):
    """Create a buy or sell order on the secondary market"""
    # Get property
    property_obj = await Property.get(order_data.property_id)
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Validate order
    if order_data.tokens <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token amount must be positive"
        )
    
    if order_data.price_per_token <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Price per token must be positive"
        )
    
    # For sell orders, check if user has enough tokens
    if order_data.order_type == OrderType.SELL:
        user_tokens = await get_user_token_balance(str(current_user.id), order_data.property_id)
        if user_tokens < order_data.tokens:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient tokens to sell"
            )
    
    # Create order
    order = MarketOrder(
        user_id=str(current_user.id),
        property_id=order_data.property_id,
        order_type=order_data.order_type,
        tokens=order_data.tokens,
        price_per_token=order_data.price_per_token,
        total_amount=order_data.tokens * order_data.price_per_token
    )
    
    await order.save()
    
    # Try to match with existing orders
    await match_orders(order)
    
    return {
        "message": "Order created successfully",
        "order_id": str(order.id),
        "status": order.status
    }


@router.get("/orders", response_model=List[OrderResponse])
async def get_market_orders(
    property_id: Optional[str] = None,
    order_type: Optional[OrderType] = None,
    limit: int = 50
):
    """Get active market orders"""
    query_filters = [MarketOrder.status == OrderStatus.ACTIVE]
    
    if property_id:
        query_filters.append(MarketOrder.property_id == property_id)
    
    if order_type:
        query_filters.append(MarketOrder.order_type == order_type)
    
    orders = await MarketOrder.find(*query_filters).sort(-MarketOrder.created_at).limit(limit).to_list()
    
    # Get property titles
    property_titles = {}
    for order in orders:
        if order.property_id not in property_titles:
            prop = await Property.get(order.property_id)
            property_titles[order.property_id] = prop.title if prop else "Unknown Property"
    
    return [
        OrderResponse(
            id=str(order.id),
            user_id=order.user_id,
            property_id=order.property_id,
            property_title=property_titles.get(order.property_id, "Unknown Property"),
            order_type=order.order_type,
            tokens=order.tokens,
            price_per_token=order.price_per_token,
            total_amount=order.total_amount,
            tokens_filled=order.tokens_filled,
            tokens_remaining=order.tokens - order.tokens_filled,
            status=order.status,
            created_at=order.created_at
        )
        for order in orders
    ]


@router.get("/orders/my", response_model=List[OrderResponse])
async def get_my_orders(
    current_user: User = Depends(get_current_verified_user)
):
    """Get current user's orders"""
    orders = await MarketOrder.find(
        MarketOrder.user_id == str(current_user.id)
    ).sort(-MarketOrder.created_at).to_list()
    
    # Get property titles
    property_titles = {}
    for order in orders:
        if order.property_id not in property_titles:
            prop = await Property.get(order.property_id)
            property_titles[order.property_id] = prop.title if prop else "Unknown Property"
    
    return [
        OrderResponse(
            id=str(order.id),
            user_id=order.user_id,
            property_id=order.property_id,
            property_title=property_titles.get(order.property_id, "Unknown Property"),
            order_type=order.order_type,
            tokens=order.tokens,
            price_per_token=order.price_per_token,
            total_amount=order.total_amount,
            tokens_filled=order.tokens_filled,
            tokens_remaining=order.tokens - order.tokens_filled,
            status=order.status,
            created_at=order.created_at
        )
        for order in orders
    ]


@router.delete("/orders/{order_id}")
async def cancel_order(
    order_id: str,
    current_user: User = Depends(get_current_verified_user)
):
    """Cancel an active order"""
    order = await MarketOrder.get(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this order"
        )
    
    if order.status != OrderStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order cannot be cancelled"
        )
    
    order.status = OrderStatus.CANCELLED
    order.updated_at = datetime.utcnow()
    await order.save()
    
    return {"message": "Order cancelled successfully"}


async def get_user_token_balance(user_id: str, property_id: str) -> int:
    """Get user's token balance for a specific property"""
    # Get all purchase transactions
    purchases = await Transaction.find(
        Transaction.user_id == user_id,
        Transaction.property_id == property_id,
        Transaction.transaction_type == "token_purchase",
        Transaction.status == TransactionStatus.COMPLETED
    ).to_list()
    
    # Get all sale transactions
    sales = await Transaction.find(
        Transaction.user_id == user_id,
        Transaction.property_id == property_id,
        Transaction.transaction_type.in_(["token_sale", "secondary_market_sell"]),
        Transaction.status == TransactionStatus.COMPLETED
    ).to_list()
    
    total_purchased = sum(tx.tokens for tx in purchases)
    total_sold = sum(tx.tokens for tx in sales)
    
    return total_purchased - total_sold


async def match_orders(new_order: MarketOrder):
    """Try to match a new order with existing orders"""
    if new_order.order_type == OrderType.BUY:
        # Find matching sell orders
        matching_orders = await MarketOrder.find(
            MarketOrder.property_id == new_order.property_id,
            MarketOrder.order_type == OrderType.SELL,
            MarketOrder.status == OrderStatus.ACTIVE,
            MarketOrder.price_per_token <= new_order.price_per_token
        ).sort(MarketOrder.price_per_token).to_list()
    else:
        # Find matching buy orders
        matching_orders = await MarketOrder.find(
            MarketOrder.property_id == new_order.property_id,
            MarketOrder.order_type == OrderType.BUY,
            MarketOrder.status == OrderStatus.ACTIVE,
            MarketOrder.price_per_token >= new_order.price_per_token
        ).sort(-MarketOrder.price_per_token).to_list()
    
    for matching_order in matching_orders:
        if new_order.tokens_filled >= new_order.tokens:
            break
        
        # Calculate trade amount
        tokens_to_trade = min(
            new_order.tokens - new_order.tokens_filled,
            matching_order.tokens - matching_order.tokens_filled
        )
        
        if tokens_to_trade <= 0:
            continue
        
        # Execute trade
        trade_price = matching_order.price_per_token  # Use existing order price
        await execute_trade(new_order, matching_order, tokens_to_trade, trade_price)


async def execute_trade(buy_order: MarketOrder, sell_order: MarketOrder, tokens: int, price_per_token: float):
    """Execute a trade between two orders"""
    try:
        # Update order fill amounts
        if buy_order.order_type == OrderType.BUY:
            buyer_order = buy_order
            seller_order = sell_order
        else:
            buyer_order = sell_order
            seller_order = buy_order
        
        buyer_order.tokens_filled += tokens
        seller_order.tokens_filled += tokens
        
        # Update order statuses
        if buyer_order.tokens_filled >= buyer_order.tokens:
            buyer_order.status = OrderStatus.FILLED
        elif buyer_order.tokens_filled > 0:
            buyer_order.status = OrderStatus.PARTIAL
        
        if seller_order.tokens_filled >= seller_order.tokens:
            seller_order.status = OrderStatus.FILLED
        elif seller_order.tokens_filled > 0:
            seller_order.status = OrderStatus.PARTIAL
        
        # Save updated orders
        await buyer_order.save()
        await seller_order.save()
        
        # Create transaction records
        total_amount = tokens * price_per_token
        
        # Buyer transaction
        buyer_tx = Transaction(
            transaction_type=TransactionType.SECONDARY_MARKET_BUY,
            status=TransactionStatus.COMPLETED,
            user_id=buyer_order.user_id,
            property_id=buyer_order.property_id,
            amount=total_amount,
            tokens=tokens,
            token_price=price_per_token,
            metadata={
                "order_id": str(buyer_order.id),
                "counterparty_order_id": str(seller_order.id),
                "trade_type": "secondary_market"
            }
        )
        
        # Seller transaction
        seller_tx = Transaction(
            transaction_type=TransactionType.SECONDARY_MARKET_SELL,
            status=TransactionStatus.COMPLETED,
            user_id=seller_order.user_id,
            property_id=seller_order.property_id,
            amount=total_amount,
            tokens=tokens,
            token_price=price_per_token,
            metadata={
                "order_id": str(seller_order.id),
                "counterparty_order_id": str(buyer_order.id),
                "trade_type": "secondary_market"
            }
        )
        
        await buyer_tx.save()
        await seller_tx.save()
        
    except Exception as e:
        print(f"Trade execution failed: {str(e)}")
        raise e