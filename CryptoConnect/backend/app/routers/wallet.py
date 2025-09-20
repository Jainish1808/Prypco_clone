"""
Wallet Management API Routes
Handles XRP wallet operations and token management
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional
from app.models.user import User
from app.auth import get_current_active_user
# from app.services.wallet_service import wallet_service
# from app.services.xrpl_service import xrpl_service
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/wallet", tags=["wallet"])


class WalletConnectRequest(BaseModel):
    address: str
    secret: str


class TokenTransferRequest(BaseModel):
    to_address: str
    token_symbol: str
    amount: float
    property_id: Optional[str] = None


@router.get("/info")
async def get_wallet_info(current_user: User = Depends(get_current_active_user)):
    """Get current user's wallet information and balance"""
    if not current_user.xrpl_wallet_address:
        raise HTTPException(
            status_code=404,
            detail="No wallet assigned to user. Please contact support."
        )
    
    try:
        # Mock wallet data for now since wallet_service is disabled
        wallet_data = {
            "xrp_balance": 10.0,
            "tokens": [],
            "explorer_url": f"https://testnet.xrpl.org/accounts/{current_user.xrpl_wallet_address}"
        }
        
        # Mock transactions
        transactions = []
        
        return {
            "address": current_user.xrpl_wallet_address,
            "xrp_balance": wallet_data.get("xrp_balance", 0),
            "tokens": wallet_data.get("tokens", []),
            "transactions": transactions,
            "explorer_url": wallet_data.get("explorer_url"),
            "sequence": wallet_data.get("sequence", 0)
        }
        
    except Exception as e:
        logger.error(f"Error getting wallet info: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch wallet information")


@router.post("/connect")
async def connect_wallet(
    wallet_request: WalletConnectRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Connect or update user's XRP wallet"""
    try:
        # Simple validation for now
        if not wallet_request.address or not wallet_request.secret:
            raise HTTPException(
                status_code=400,
                detail="Invalid wallet credentials. Address and secret required."
            )
        
        # Update user's wallet information
        current_user.xrpl_wallet_address = wallet_request.address
        current_user.xrpl_wallet_seed = wallet_request.secret  # In production, encrypt this
        await current_user.save()
        
        # Mock wallet balance
        wallet_data = {"xrp_balance": 10.0}
        
        logger.info(f"User {current_user.username} connected wallet {wallet_request.address}")
        
        return {
            "message": "Wallet connected successfully",
            "address": wallet_request.address,
            "xrp_balance": wallet_data.get("xrp_balance", 0),
            "explorer_url": f"https://testnet.xrpl.org/accounts/{wallet_request.address}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error connecting wallet: {e}")
        raise HTTPException(status_code=500, detail="Failed to connect wallet")


@router.post("/transfer")
async def transfer_tokens(
    transfer_request: TokenTransferRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Transfer property tokens to another wallet"""
    if not current_user.xrpl_wallet_address or not current_user.xrpl_wallet_seed:
        raise HTTPException(
            status_code=400,
            detail="No wallet connected. Please connect your XRP wallet first."
        )
    
    try:
        # Mock token transfer for now
        result = {
            "success": True,
            "tx_hash": f"mock_transfer_{transfer_request.token_symbol}_{transfer_request.amount}"
        }
        
        if result["success"]:
            logger.info(f"Token transfer successful: {result['tx_hash']}")
            return {
                "success": True,
                "message": "Tokens transferred successfully",
                "transaction_hash": result["tx_hash"],
                "explorer_url": f"https://testnet.xrpl.org/transactions/{result['tx_hash']}",
                "amount": transfer_request.amount,
                "token": transfer_request.token_symbol,
                "to_address": transfer_request.to_address
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Transfer failed: {result.get('error', 'Unknown error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error transferring tokens: {e}")
        raise HTTPException(status_code=500, detail="Failed to transfer tokens")


@router.get("/tokens")
async def get_user_tokens(current_user: User = Depends(get_current_active_user)):
    """Get all property tokens owned by the user"""
    if not current_user.xrpl_wallet_address:
        raise HTTPException(
            status_code=404,
            detail="No wallet assigned to user"
        )
    
    try:
        # Mock wallet data
        wallet_data = {
            "tokens": []
        }
        
        # Format token data with additional property information
        tokens = []
        for token in wallet_data.get("tokens", []):
            # Try to get property information for this token
            property_info = await get_property_by_token_symbol(token["currency"])
            
            tokens.append({
                "symbol": token["currency"],
                "balance": token["balance"],
                "issuer": token["issuer"],
                "property_info": property_info,
                "explorer_url": f"https://testnet.xrpl.org/accounts/{current_user.xrpl_wallet_address}"
            })
        
        return {
            "wallet_address": current_user.xrpl_wallet_address,
            "tokens": tokens,
            "total_tokens": len(tokens)
        }
        
    except Exception as e:
        logger.error(f"Error getting user tokens: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user tokens")


@router.post("/create-trustline")
async def create_trustline(
    token_symbol: str,
    issuer_address: str,
    current_user: User = Depends(get_current_active_user)
):
    """Create a trust line to hold a specific property token"""
    if not current_user.xrpl_wallet_seed:
        raise HTTPException(
            status_code=400,
            detail="No wallet connected. Please connect your XRP wallet first."
        )
    
    try:
        # Mock trust line creation
        tx_hash = f"mock_trustline_{token_symbol}_{issuer_address[:8]}"
        
        if tx_hash:
            return {
                "success": True,
                "message": "Trust line created successfully",
                "transaction_hash": tx_hash,
                "explorer_url": f"https://testnet.xrpl.org/transactions/{tx_hash}",
                "token_symbol": token_symbol,
                "issuer": issuer_address
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to create trust line"
            )
            
    except Exception as e:
        logger.error(f"Error creating trust line: {e}")
        raise HTTPException(status_code=500, detail="Failed to create trust line")


@router.post("/assign-to-existing-users")
async def assign_wallets_to_existing_users():
    """Assign your 4 XRP wallets to existing users in database"""
    try:
        # Mock wallet assignment
        success = True
        
        if success:
            return {
                "success": True,
                "message": "XRP wallets assigned to existing users successfully",
                "wallets_assigned": 4,
                "explorer_links": [
                    "https://testnet.xrpl.org/accounts/rqhB5Kp6YQZbx7Zbx7Pxm3FdGp2yqtQ5A",
                    "https://testnet.xrpl.org/accounts/rnDmRyDdBqCbkGWSnKzySZqtRqVJyDrFg",
                    "https://testnet.xrpl.org/accounts/rLBBNiA8MdTSGBBXZu3vwysZp5uEryU85",
                    "https://testnet.xrpl.org/accounts/rJ86bTZkm5SiAwV68ZJfq9SdJSwM5DAw1"
                ]
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to assign wallets. Make sure users exist in database."
            )
            
    except Exception as e:
        logger.error(f"Error in wallet assignment endpoint: {e}")
        raise HTTPException(status_code=500, detail="Failed to assign wallets")


async def get_property_by_token_symbol(token_symbol: str) -> Optional[Dict]:
    """Helper function to get property information by token symbol"""
    try:
        from app.models.property import Property
        
        property_doc = await Property.find_one(Property.token_symbol == token_symbol)
        if property_doc:
            return {
                "id": str(property_doc.id),
                "title": property_doc.title,
                "city": property_doc.city,
                "country": property_doc.country,
                "total_value": property_doc.total_value,
                "size_sqm": property_doc.size_sqm
            }
        return None
        
    except Exception as e:
        logger.error(f"Error getting property by token symbol: {e}")
        return None