from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from datetime import datetime
from app.models.property import Property
from app.models.user import User
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.auth import get_current_active_user, get_current_user
from app.services.xrpl_service import xrpl_service
from pydantic import BaseModel
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tokens", tags=["tokens"])


class TokenTransferRequest(BaseModel):
    property_id: str
    to_address: str  # XRP address to send tokens to
    amount: int  # Number of tokens to transfer
    memo: Optional[str] = None


class TokenBalanceResponse(BaseModel):
    currency: str
    issuer: str
    balance: float
    property_id: Optional[str] = None
    property_title: Optional[str] = None


class UserTokensResponse(BaseModel):
    xrpl_address: str
    total_tokens: int
    tokens: List[TokenBalanceResponse]


class TokenTransferResponse(BaseModel):
    success: bool
    tx_hash: Optional[str] = None
    explorer_url: Optional[str] = None
    from_address: str
    to_address: str
    amount: int
    token_symbol: str
    message: str


@router.get("/my-tokens", response_model=UserTokensResponse)
async def get_user_tokens(current_user: User = Depends(get_current_user)):
    """Get all XRP tokens owned by the current user"""
    try:
        if not current_user.xrpl_wallet_address:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User does not have an XRP wallet address"
            )
        
        # Get all tokens from XRPL
        user_tokens = await xrpl_service.get_all_user_tokens(current_user.xrpl_wallet_address)
        
        # Enrich with property information
        enriched_tokens = []
        total_token_count = 0
        
        for token in user_tokens:
            # Find the property associated with this token
            property_obj = await Property.find_one(
                Property.token_symbol == token["currency"],
                Property.xrpl_issuer_address == token["issuer"]
            )
            
            enriched_token = TokenBalanceResponse(
                currency=token["currency"],
                issuer=token["issuer"],
                balance=token["balance"],
                property_id=str(property_obj.id) if property_obj else None,
                property_title=property_obj.title if property_obj else None
            )
            
            enriched_tokens.append(enriched_token)
            total_token_count += int(token["balance"])
        
        return UserTokensResponse(
            xrpl_address=current_user.xrpl_wallet_address,
            total_tokens=total_token_count,
            tokens=enriched_tokens
        )
        
    except Exception as e:
        logger.error(f"Error getting user tokens: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user tokens: {str(e)}"
        )


@router.post("/transfer", response_model=TokenTransferResponse)
async def transfer_tokens(
    transfer_request: TokenTransferRequest,
    current_user: User = Depends(get_current_user)
):
    """Transfer property tokens to another user"""
    try:
        # Validate user has XRP wallet
        if not current_user.xrpl_wallet_address or not current_user.xrpl_wallet_seed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User does not have a properly configured XRP wallet"
            )
        
        # Get property information
        property_obj = await Property.get(transfer_request.property_id)
        if not property_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found"
            )
        
        if not property_obj.xrpl_token_created:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Property tokens are not yet created on XRP Ledger"
            )
        
        # Check if user has enough tokens
        user_balance = await xrpl_service.get_token_balance(
            current_user.xrpl_wallet_address,
            property_obj.token_symbol,
            property_obj.xrpl_issuer_address
        )
        
        if user_balance < transfer_request.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient tokens. You have {user_balance}, trying to transfer {transfer_request.amount}"
            )
        
        # Perform the transfer
        transfer_result = await xrpl_service.transfer_tokens_user_to_user(
            from_wallet_seed=current_user.xrpl_wallet_seed,
            to_address=transfer_request.to_address,
            token_symbol=property_obj.token_symbol,
            issuer_address=property_obj.xrpl_issuer_address,
            amount=str(transfer_request.amount),
            memo=transfer_request.memo or f"Transfer of {property_obj.title} tokens"
        )
        
        if transfer_result:
            # Create transaction record
            transaction = Transaction(
                transaction_type=TransactionType.TOKEN_TRANSFER,
                status=TransactionStatus.COMPLETED,
                user_id=str(current_user.id),
                property_id=str(property_obj.id),
                amount=0,  # No money involved, just token transfer
                tokens=transfer_request.amount,
                token_price=property_obj.token_price,
                xrpl_tx_hash=transfer_result["tx_hash"],
                xrpl_from_address=current_user.xrpl_wallet_address,
                xrpl_to_address=transfer_request.to_address,
                metadata={
                    "memo": transfer_request.memo,
                    "transfer_type": "user_to_user"
                }
            )
            
            await transaction.save()
            
            return TokenTransferResponse(
                success=True,
                tx_hash=transfer_result["tx_hash"],
                explorer_url=transfer_result["explorer_url"],
                from_address=transfer_result["from_address"],
                to_address=transfer_result["to_address"],
                amount=transfer_request.amount,
                token_symbol=property_obj.token_symbol,
                message=f"Successfully transferred {transfer_request.amount} {property_obj.token_symbol} tokens"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token transfer failed on XRP Ledger"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error transferring tokens: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to transfer tokens: {str(e)}"
        )


@router.get("/verify/{token_symbol}")
async def verify_token_on_ledger(token_symbol: str, issuer_address: str):
    """Verify token existence and get details from XRP Ledger"""
    try:
        token_info = await xrpl_service.verify_token_on_ledger(token_symbol, issuer_address)
        
        if not token_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Token not found on XRP Ledger"
            )
        
        # Get associated property information
        property_obj = await Property.find_one(
            Property.token_symbol == token_symbol,
            Property.xrpl_issuer_address == issuer_address
        )
        
        result = {
            **token_info,
            "property_info": None
        }
        
        if property_obj:
            result["property_info"] = {
                "id": str(property_obj.id),
                "title": property_obj.title,
                "address": property_obj.address,
                "total_value": property_obj.total_value,
                "creation_tx": property_obj.xrpl_creation_tx_hash,
                "explorer_url": property_obj.xrpl_explorer_url
            }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify token: {str(e)}"
        )


@router.get("/transaction/{tx_hash}")
async def get_transaction_details(tx_hash: str):
    """Get detailed transaction information from XRP Ledger"""
    try:
        tx_details = await xrpl_service.get_transaction_details(tx_hash)
        
        if not tx_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        return tx_details
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transaction details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get transaction details: {str(e)}"
        )


@router.get("/property/{property_id}/holders")
async def get_property_token_holders(property_id: str):
    """Get all current holders of a property's tokens"""
    try:
        property_obj = await Property.get(property_id)
        if not property_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found"
            )
        
        if not property_obj.xrpl_token_created:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Property is not tokenized yet"
            )
        
        # Get token verification info which includes holders
        token_info = await xrpl_service.verify_token_on_ledger(
            property_obj.token_symbol,
            property_obj.xrpl_issuer_address
        )
        
        if token_info and token_info.get("holders"):
            # Enrich holder information with user data if available
            enriched_holders = []
            for holder in token_info["holders"]:
                user = await User.find_one(User.xrpl_wallet_address == holder["address"])
                enriched_holder = {
                    **holder,
                    "user_info": {
                        "username": user.username if user else "Unknown",
                        "name": f"{user.first_name or ''} {user.last_name or ''}".strip() if user else "Unknown"
                    } if user else None
                }
                enriched_holders.append(enriched_holder)
            
            return {
                "property_id": property_id,
                "property_title": property_obj.title,
                "token_symbol": property_obj.token_symbol,
                "total_supply": token_info.get("total_supply", "0"),
                "holders": enriched_holders
            }
        
        return {
            "property_id": property_id,
            "property_title": property_obj.title,
            "token_symbol": property_obj.token_symbol,
            "total_supply": "0",
            "holders": []
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting token holders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get token holders: {str(e)}"
        )