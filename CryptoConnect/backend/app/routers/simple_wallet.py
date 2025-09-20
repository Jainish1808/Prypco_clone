"""
Simple Wallet API Routes
Basic wallet info without complex XRPL imports
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional
from app.models.user import User
from app.auth import get_current_active_user
import logging
import time

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/simple-wallet", tags=["simple-wallet"])


@router.get("/info")
async def get_simple_wallet_info(current_user: User = Depends(get_current_active_user)):
    """Get basic wallet information for current user"""
    try:
        if not current_user.xrpl_wallet_address:
            raise HTTPException(
                status_code=404,
                detail="No wallet assigned to user"
            )
        
        # Get real user properties to show as tokens
        from app.models.property import Property
        user_properties = await Property.find(Property.seller_id == str(current_user.id)).to_list()
        
        # Convert properties to token format
        tokens = []
        for prop in user_properties:
            if hasattr(prop, 'token_symbol') and prop.token_symbol:
                tokens.append({
                    "symbol": prop.token_symbol,
                    "balance": prop.total_tokens if hasattr(prop, 'total_tokens') else prop.size_sqm * 10000,
                    "issuer": current_user.xrpl_wallet_address,
                    "property_info": {
                        "id": str(prop.id),
                        "title": prop.title,
                        "city": prop.city,
                        "country": prop.country
                    }
                })
        
        wallet_info = {
            "address": current_user.xrpl_wallet_address,
            "xrp_balance": 10.0,  # Keep mock balance for now
            "tokens": tokens,
            "transactions": [
                {
                    "hash": f"TX_{current_user.username}_{len(tokens)}",
                    "type": "TokenCreation" if tokens else "Payment",
                    "date": int(time.time()) - 3600,  # 1 hour ago
                    "amount": str(len(tokens) * 1000) if tokens else "10",
                    "destination": current_user.xrpl_wallet_address,
                    "explorer_url": f"https://testnet.xrpl.org/transactions/TX_{current_user.username}_{len(tokens)}"
                }
            ] if tokens else [],
            "explorer_url": f"https://testnet.xrpl.org/accounts/{current_user.xrpl_wallet_address}"
        }
        
        return wallet_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting wallet info: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch wallet information")


@router.get("/balance")
async def get_wallet_balance(current_user: User = Depends(get_current_active_user)):
    """Get wallet balance summary"""
    try:
        if not current_user.xrpl_wallet_address:
            return {"xrp_balance": 0, "token_count": 0, "has_wallet": False}
        
        return {
            "xrp_balance": 10.0,
            "token_count": 1,
            "has_wallet": True,
            "address": current_user.xrpl_wallet_address
        }
        
    except Exception as e:
        logger.error(f"Error getting wallet balance: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch wallet balance")