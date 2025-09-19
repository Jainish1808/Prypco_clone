from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.models.transaction import Transaction, TransactionResponse, UserHolding, IncomeStatement, TransactionType, TransactionStatus
from app.models.property import Property
from app.models.user import User
from app.auth import get_current_verified_user, get_current_active_user, get_current_user
from app.services.xrpl_service import xrpl_service

router = APIRouter(prefix="/api/investor", tags=["investor"])


@router.get("/holdings")
async def get_user_holdings(current_user: User = Depends(get_current_user)):
    """Get current user's token holdings - KYC not required for viewing"""
    try:
        # Get all purchase transactions for the user
        purchase_transactions = await Transaction.find(
            Transaction.user_id == str(current_user.id),
            Transaction.transaction_type.in_(["token_purchase", "secondary_market_buy"]),
            Transaction.status == TransactionStatus.COMPLETED
        ).to_list()
        
        # Get all sale transactions for the user
        sale_transactions = await Transaction.find(
            Transaction.user_id == str(current_user.id),
            Transaction.transaction_type.in_(["token_sale", "secondary_market_sell"]),
            Transaction.status == TransactionStatus.COMPLETED
        ).to_list()
        
        # Group by property and calculate holdings
        property_holdings = {}
        
        # Add purchases
        for tx in purchase_transactions:
            if tx.property_id not in property_holdings:
                property_holdings[tx.property_id] = {
                    "tokens": 0,
                    "total_investment": 0.0
                }
            property_holdings[tx.property_id]["tokens"] += tx.tokens
            property_holdings[tx.property_id]["total_investment"] += tx.amount
        
        # Subtract sales
        for tx in sale_transactions:
            if tx.property_id in property_holdings:
                property_holdings[tx.property_id]["tokens"] -= tx.tokens
                # Proportionally reduce investment
                if property_holdings[tx.property_id]["tokens"] > 0:
                    reduction_ratio = tx.tokens / (property_holdings[tx.property_id]["tokens"] + tx.tokens)
                    property_holdings[tx.property_id]["total_investment"] *= (1 - reduction_ratio)
        
        # Convert to response format
        holdings = []
        for property_id, holding in property_holdings.items():
            if holding["tokens"] > 0:  # Only include properties with positive holdings
                try:
                    property_obj = await Property.get(property_id)
                    if property_obj:
                        holdings.append({
                            "property_id": property_id,
                            "property_title": property_obj.title,
                            "tokens": holding["tokens"],
                            "total_investment": holding["total_investment"],
                            "current_value": holding["tokens"] * property_obj.token_price,
                            "property_status": property_obj.status
                        })
                except Exception as e:
                    print(f"Error fetching property {property_id}: {e}")
                    continue
        
        return holdings
    except Exception as e:
        return []  # Return empty list if any error occurs
    
    # Get all sale transactions for the user
    sale_transactions = await Transaction.find(
        Transaction.user_id == str(current_user.id),
        Transaction.transaction_type.in_(["token_sale", "secondary_market_sell"]),
        Transaction.status == TransactionStatus.COMPLETED
    ).to_list()
    
    # Group by property and calculate holdings
    property_holdings = {}
    
    # Add purchases
    for tx in purchase_transactions:
        if tx.property_id not in property_holdings:
            property_holdings[tx.property_id] = {
                "tokens": 0,
                "total_investment": 0.0
            }
        property_holdings[tx.property_id]["tokens"] += tx.tokens
        property_holdings[tx.property_id]["total_investment"] += tx.amount
    
    # Subtract sales
    for tx in sale_transactions:
        if tx.property_id in property_holdings:
            property_holdings[tx.property_id]["tokens"] -= tx.tokens
            # Proportionally reduce investment
            if property_holdings[tx.property_id]["tokens"] > 0:
                reduction_ratio = tx.tokens / (property_holdings[tx.property_id]["tokens"] + tx.tokens)
                property_holdings[tx.property_id]["total_investment"] *= (1 - reduction_ratio)
    
    # Get property details and calculate current values
    holdings = []
    for property_id, holding_data in property_holdings.items():
        if holding_data["tokens"] <= 0:
            continue
            
        property_obj = await Property.get(property_id)
        if property_obj:
            current_value = holding_data["tokens"] * property_obj.token_price
            ownership_percentage = (holding_data["tokens"] / property_obj.total_tokens) * 100 if property_obj.total_tokens > 0 else 0
            
            # Calculate monthly rental income
            monthly_rental_income = 0.0
            if property_obj.monthly_rent and property_obj.total_tokens > 0:
                monthly_rental_income = (holding_data["tokens"] / property_obj.total_tokens) * property_obj.monthly_rent
            
            holdings.append(UserHolding(
                property_id=property_id,
                property_title=property_obj.title,
                tokens_owned=holding_data["tokens"],
                total_investment=holding_data["total_investment"],
                current_value=current_value,
                ownership_percentage=ownership_percentage,
                monthly_rental_income=monthly_rental_income
            ))
    
    return holdings


@router.get("/transactions")
async def get_user_transactions(current_user: User = Depends(get_current_user)):
    """Get user's transaction history"""
    try:
        transactions = await Transaction.find(
            Transaction.user_id == str(current_user.id)
        ).sort(-Transaction.created_at).to_list()
        
        result = []
        for tx in transactions:
            result.append({
                "id": str(tx.id),
                "transaction_type": tx.transaction_type,
                "status": tx.status,
                "user_id": tx.user_id,
                "property_id": tx.property_id,
                "amount": tx.amount,
                "tokens": tx.tokens,
                "token_price": tx.token_price,
                "xrpl_tx_hash": tx.xrpl_tx_hash,
                "created_at": tx.created_at.isoformat() if tx.created_at else None,
                "completed_at": tx.completed_at.isoformat() if tx.completed_at else None
            })
        
        return result
    except Exception as e:
        return []  # Return empty list if any error occurs


@router.get("/income-statements")
async def get_income_statements(current_user: User = Depends(get_current_user)):
    """Get user's rental income statements"""
    try:
        # Get rental distribution transactions
        rental_transactions = await Transaction.find(
            Transaction.user_id == str(current_user.id),
            Transaction.transaction_type == "rental_distribution",
            Transaction.status == TransactionStatus.COMPLETED
        ).sort(-Transaction.created_at).to_list()
        
        statements = []
        for tx in rental_transactions:
            try:
                property_obj = await Property.get(tx.property_id)
                if property_obj:
                    # Extract period from metadata or use transaction date
                    period = tx.metadata.get("period") if tx.metadata else tx.created_at.strftime("%Y-%m")
                    
                    statements.append({
                        "property_id": tx.property_id,
                        "property_title": property_obj.title,
                        "period": period,
                        "amount": tx.amount,
                        "tokens": tx.tokens,
                        "payment_date": tx.completed_at.isoformat() if tx.completed_at else tx.created_at.isoformat()
                    })
            except Exception as e:
                continue  # Skip problematic transactions
        
        return statements
    except Exception as e:
        return []  # Return empty list if any error occurs


@router.get("/portfolio-summary")
async def get_portfolio_summary(current_user: User = Depends(get_current_user)):
    """Get user's portfolio summary"""
    # Get holdings
    holdings = await get_user_holdings(current_user)
    
    # Calculate totals
    total_investment = sum(holding.total_investment for holding in holdings)
    total_current_value = sum(holding.current_value for holding in holdings)
    total_monthly_income = sum(holding.monthly_rental_income for holding in holdings)
    
    # Get recent transactions
    recent_transactions = await Transaction.find(
        Transaction.user_id == str(current_user.id)
    ).sort(-Transaction.created_at).limit(5).to_list()
    
    return {
        "total_investment": total_investment,
        "total_current_value": total_current_value,
        "total_monthly_income": total_monthly_income,
        "annual_income": total_monthly_income * 12,
        "portfolio_yield": (total_monthly_income * 12 / total_investment * 100) if total_investment > 0 else 0,
        "properties_count": len(holdings),
        "recent_transactions": [
            {
                "id": str(tx.id),
                "type": tx.transaction_type,
                "amount": tx.amount,
                "tokens": tx.tokens,
                "date": tx.created_at
            }
            for tx in recent_transactions
        ]
    }