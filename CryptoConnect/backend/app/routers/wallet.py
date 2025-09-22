from fastapi import APIRouter, Depends, HTTPException, status
from app.auth import get_current_user
from app.models.user import User
from app.services.xrpl_service import xrpl_service

router = APIRouter(prefix="/api/wallet", tags=["wallet"])

@router.post("/fund")
async def fund_wallet(current_user: User = Depends(get_current_user)):
    """Fund the user's testnet wallet using the faucet."""
    if not current_user.xrpl_wallet_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not have an XRP wallet address."
        )

    if settings.xrpl_network != "testnet":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wallet funding is only available on the testnet."
        )

    try:
        success = await xrpl_service._fund_wallet(current_user.xrpl_wallet_address)
        if success:
            return {"message": "Wallet funded successfully."}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fund wallet."
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fund wallet: {e}"
        )
