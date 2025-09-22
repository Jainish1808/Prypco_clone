from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings
from app.models.user import User

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token handling
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get the current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    from bson import ObjectId

    if not ObjectId.is_valid(user_id):
        # If the ID from the token is not a valid ObjectId, then it's a bad token.
        raise credentials_exception
    
    user = await User.get(ObjectId(user_id))
        
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_verified_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Get the current KYC verified user"""
    if not current_user.is_kyc_verified:
        raise HTTPException(status_code=400, detail="User not KYC verified")
    return current_user


async def get_current_seller(current_user: User = Depends(get_current_active_user)) -> User:
    """Get the current seller user (or admin)"""
    from app.models.user import UserRole
    if current_user.role not in [UserRole.SELLER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail=f"Access denied: Seller access required. Current role: {current_user.role}")
    return current_user


async def get_current_investor(current_user: User = Depends(get_current_active_user)) -> User:
    """Get the current investor user (or admin)"""
    from app.models.user import UserRole
    if current_user.role not in [UserRole.INVESTOR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail=f"Access denied: Investor access required. Current role: {current_user.role}")
    return current_user


async def get_current_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Get the current admin user"""
    from app.models.user import UserRole
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Access denied: Admin access required")
    return current_user