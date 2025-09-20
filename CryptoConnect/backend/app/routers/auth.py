from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from app.models.user import User, UserCreate, UserLogin, UserResponse, KYCSubmission, UserRole
from app.auth import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    get_current_active_user
)
from app.config import settings
# from app.services.wallet_service import wallet_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["authentication"])


@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    """Register a new user"""
    # Check if user already exists
    existing_user = await User.find_one(User.email == user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    existing_username = await User.find_one(User.username == user_data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    
    # Map frontend fields to backend fields
    role = UserRole.INVESTOR
    if user_data.userType == "seller":
        role = UserRole.SELLER
    elif user_data.role:  # Backward compatibility
        role = user_data.role
    
    first_name = user_data.firstName or user_data.first_name
    last_name = user_data.lastName or user_data.last_name
    
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        role=role,
        first_name=first_name,
        last_name=last_name
    )
    
    # XRP wallet assignment temporarily disabled
    # Will be assigned manually using the database script
    
    await user.save()
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        firstName=user.first_name,
        lastName=user.last_name,
        walletAddress=user.xrpl_wallet_address,
        isKYCVerified=user.is_kyc_verified,
        userType=user.role.value,
        createdAt=user.created_at,
        role=user.role,
        is_active=user.is_active,
        kyc_status=user.kyc_status,
        phone=user.phone
    )


@router.post("/login")
async def login_user(user_data: UserLogin):
    """Authenticate user and return JWT token"""
    # Find user by username or email (more flexible approach)
    user = None
    
    # Try to find by username first
    user = await User.find_one(User.username == user_data.username)
    
    # If not found and the username looks like an email, try email search
    if not user and "@" in user_data.username:
        user = await User.find_one(User.email == user_data.username)
    
    # Fallback to email field if provided
    if not user and user_data.email:
        user = await User.find_one(User.email == user_data.email)
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.jwt_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            firstName=user.first_name,
            lastName=user.last_name,
            walletAddress=user.xrpl_wallet_address,
            isKYCVerified=user.is_kyc_verified,
            userType=user.role.value,
            createdAt=user.created_at,
            role=user.role,
            is_active=user.is_active,
            kyc_status=user.kyc_status,
            phone=user.phone
        )
    }


@router.get("/user", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
        firstName=current_user.first_name,
        lastName=current_user.last_name,
        walletAddress=current_user.xrpl_wallet_address,
        isKYCVerified=current_user.is_kyc_verified,
        userType=current_user.role.value,
        createdAt=current_user.created_at,
        role=current_user.role,
        is_active=current_user.is_active,
        kyc_status=current_user.kyc_status,
        phone=current_user.phone
    )


@router.post("/kyc-submit")
async def submit_kyc(
    kyc_data: KYCSubmission,
    current_user: User = Depends(get_current_active_user)
):
    """Submit KYC information"""
    # Update user with KYC data
    current_user.first_name = kyc_data.first_name
    current_user.last_name = kyc_data.last_name
    current_user.phone = kyc_data.phone
    current_user.kyc_data = kyc_data.dict()
    current_user.kyc_status = "verified"  # Simplified - auto-approve for demo
    current_user.is_kyc_verified = True
    
    await current_user.save()
    
    return {"message": "KYC submitted successfully", "status": "verified"}


@router.post("/logout")
async def logout_user(current_user: User = Depends(get_current_active_user)):
    """Logout user (for session-based auth, this would clear session)"""
    # Since we're using JWT tokens, logout is handled client-side
    # But we return success for compatibility
    return {"message": "Logged out successfully"}