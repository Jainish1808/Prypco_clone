from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from bson import ObjectId
from app.models.property import Property, PropertyResponse, PropertyUpdateAdmin
from app.models.user import User
from app.auth import get_current_admin
from app.services.tokenization_service import tokenization_service

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/properties/pending", response_model=List[PropertyResponse])
async def get_pending_properties(current_user: User = Depends(get_current_admin)):
    """Get all properties pending review"""
    properties = await Property.find(
        Property.status == "pending_review"
    ).to_list()
    
    return [
        PropertyResponse(
            id=str(prop.id),
            title=prop.title,
            description=prop.description,
            address=prop.address,
            city=prop.city,
            country=prop.country,
            property_type=prop.property_type,
            total_value=prop.total_value,
            size_sqm=prop.size_sqm,
            total_tokens=prop.total_tokens,
            token_price=prop.token_price,
            tokens_sold=prop.tokens_sold,
            bedrooms=prop.bedrooms,
            bathrooms=prop.bathrooms,
            parking_spaces=prop.parking_spaces,
            year_built=prop.year_built,
            monthly_rent=prop.monthly_rent,
            annual_yield=prop.annual_yield,
            seller_name=prop.seller_name,
            status=prop.status,
            images=prop.images,
            created_at=prop.created_at
        )
        for prop in properties
    ]


@router.put("/properties/{property_id}/status")
async def update_property_status(
    property_id: str,
    update_data: PropertyUpdateAdmin,
    current_user: User = Depends(get_current_admin)
):
    """Update property status (approve/reject)"""
    property_obj = await Property.get(property_id)
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Update status
    if update_data.status:
        property_obj.status = update_data.status
        if update_data.status == "approved":
            property_obj.approved_at = property_obj.updated_at
    
    if update_data.admin_notes:
        property_obj.admin_notes = update_data.admin_notes
    
    await property_obj.save()
    
    return {"message": "Property status updated successfully"}


@router.post("/properties/{property_id}/tokenize")
async def tokenize_property(
    property_id: str,
    current_user: User = Depends(get_current_admin)
):
    """Manually trigger property tokenization"""
    property_obj = await Property.get(property_id)
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    if property_obj.status != "approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Property must be approved before tokenization"
        )
    
    if property_obj.xrpl_token_created:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Property already tokenized"
        )
    
    # Tokenize property
    success = await tokenization_service.tokenize_property(property_obj)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to tokenize property"
        )
    
    return {
        "message": "Property tokenized successfully",
        "token_symbol": property_obj.token_symbol,
        "xrpl_tx_hash": property_obj.xrpl_creation_tx_hash
    }


@router.post("/properties/{property_id}/distribute-income")
async def distribute_rental_income(
    property_id: str,
    rental_income: float,
    current_user: User = Depends(get_current_admin)
):
    """Distribute rental income to token holders"""
    property_obj = await Property.get(property_id)
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    if not property_obj.xrpl_token_created:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Property not tokenized yet"
        )
    
    if rental_income <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rental income must be positive"
        )
    
    # Distribute income
    success = await tokenization_service.distribute_rental_income(property_obj, rental_income)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to distribute rental income"
        )
    
    return {"message": "Rental income distributed successfully"}


@router.get("/dashboard")
async def get_admin_dashboard(current_user: User = Depends(get_current_admin)):
    """Get admin dashboard statistics"""
    # Count properties by status
    pending_count = await Property.find(Property.status == "pending_review").count()
    approved_count = await Property.find(Property.status == "approved").count()
    tokenized_count = await Property.find(Property.status == "tokenized").count()
    sold_out_count = await Property.find(Property.status == "sold_out").count()
    
    # Count users
    total_users = await User.find().count()
    verified_users = await User.find(User.is_kyc_verified == True).count()
    
    return {
        "properties": {
            "pending_review": pending_count,
            "approved": approved_count,
            "tokenized": tokenized_count,
            "sold_out": sold_out_count,
            "total": pending_count + approved_count + tokenized_count + sold_out_count
        },
        "users": {
            "total": total_users,
            "verified": verified_users,
            "unverified": total_users - verified_users
        }
    }


@router.get("/properties")
async def get_all_properties(current_user: User = Depends(get_current_admin)):
    """Get all properties for admin review"""
    try:
        properties = await Property.find().to_list()
        
        property_list = []
        for prop in properties:
            # Convert property to dict with safe field access
            prop_dict = {
                "id": str(prop.id),
                "title": getattr(prop, 'title', ''),
                "description": getattr(prop, 'description', ''),
                "address": getattr(prop, 'address', ''),
                "city": getattr(prop, 'city', ''),
                "country": getattr(prop, 'country', ''),
                "property_type": str(getattr(prop, 'property_type', 'apartment')),
                "total_value": getattr(prop, 'total_value', 0),
                "size_sqm": getattr(prop, 'size_sqm', 0),
                "total_tokens": getattr(prop, 'total_tokens', 0),
                "token_price": getattr(prop, 'token_price', 0),
                "tokens_sold": getattr(prop, 'tokens_sold', 0),
                "bedrooms": getattr(prop, 'bedrooms', None),
                "bathrooms": getattr(prop, 'bathrooms', None),
                "parking_spaces": getattr(prop, 'parking_spaces', None),
                "year_built": getattr(prop, 'year_built', None),
                "monthly_rent": getattr(prop, 'monthly_rent', None),
                "annual_yield": getattr(prop, 'annual_yield', None),
                "status": getattr(prop, 'status', 'pending_review'),
                "images": getattr(prop, 'images', []),
                "created_at": prop.created_at.isoformat() if hasattr(prop, 'created_at') and prop.created_at else None,
                "seller_name": getattr(prop, 'seller_name', 'Unknown Seller'),
                "seller_id": getattr(prop, 'seller_id', None),
                "seller_email": getattr(prop, 'seller_email', None)
            }
            
            property_list.append(prop_dict)
        
        return property_list
    except Exception as e:
        import traceback
        print(f"Error in get_all_properties: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching properties: {str(e)}"
        )


@router.post("/properties/{property_id}/approve")
async def approve_property(
    property_id: str,
    current_user: User = Depends(get_current_admin)
):
    """Approve a property for tokenization"""
    try:
        property_obj = await Property.get(ObjectId(property_id))
        if not property_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found"
            )
        
        if property_obj.status != "pending_review":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Property is not in pending review status"
            )
        
        property_obj.status = "approved"
        await property_obj.save()
        
        return {"message": "Property approved successfully", "property_id": property_id}
    
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid property ID format"
        )


@router.post("/properties/{property_id}/reject")
async def reject_property(
    property_id: str,
    current_user: User = Depends(get_current_admin)
):
    """Reject a property"""
    try:
        property_obj = await Property.get(ObjectId(property_id))
        if not property_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found"
            )
        
        if property_obj.status != "pending_review":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Property is not in pending review status"
            )
        
        property_obj.status = "rejected"
        await property_obj.save()
        
        return {"message": "Property rejected successfully", "property_id": property_id}
    
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid property ID format"
        )


@router.get("/properties/{property_id}")
async def get_property_for_admin(
    property_id: str,
    current_user: User = Depends(get_current_admin)
):
    """Get detailed information about a specific property for admin"""
    try:
        if ObjectId.is_valid(property_id):
            property_obj = await Property.get(ObjectId(property_id))
        else:
            property_obj = await Property.get(property_id)
            
        if not property_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found"
            )
        
        # Return property data in the same format as the properties list
        return {
            "id": str(property_obj.id),
            "title": getattr(property_obj, 'title', ''),
            "description": getattr(property_obj, 'description', ''),
            "address": getattr(property_obj, 'address', ''),
            "city": getattr(property_obj, 'city', ''),
            "country": getattr(property_obj, 'country', ''),
            "property_type": str(getattr(property_obj, 'property_type', 'apartment')),
            "total_value": getattr(property_obj, 'total_value', 0),
            "size_sqm": getattr(property_obj, 'size_sqm', 0),
            "total_tokens": getattr(property_obj, 'total_tokens', 0),
            "token_price": getattr(property_obj, 'token_price', 0),
            "tokens_sold": getattr(property_obj, 'tokens_sold', 0),
            "bedrooms": getattr(property_obj, 'bedrooms', None),
            "bathrooms": getattr(property_obj, 'bathrooms', None),
            "parking_spaces": getattr(property_obj, 'parking_spaces', None),
            "year_built": getattr(property_obj, 'year_built', None),
            "monthly_rent": getattr(property_obj, 'monthly_rent', None),
            "annual_yield": getattr(property_obj, 'annual_yield', None),
            "status": getattr(property_obj, 'status', 'pending_review'),
            "images": getattr(property_obj, 'images', []),
            "created_at": property_obj.created_at.isoformat() if hasattr(property_obj, 'created_at') and property_obj.created_at else None,
            "seller_name": getattr(property_obj, 'seller_name', 'Unknown Seller'),
            "seller_id": getattr(property_obj, 'seller_id', None),
            "seller_email": getattr(property_obj, 'seller_email', None)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching property: {str(e)}"
        )


@router.get("/users", response_model=List[dict])
async def get_all_users(current_user: User = Depends(get_current_admin)):
    """Get all users for admin management"""
    try:
        users = await User.find().to_list()
        user_list = []
        
        for user in users:
            user_dict = {
                "id": str(user.id),
                "firstName": getattr(user, 'first_name', None),
                "lastName": getattr(user, 'last_name', None),
                "username": getattr(user, 'username', ''),
                "email": str(getattr(user, 'email', '')),
                "userType": str(getattr(user, 'role', 'investor')),
                "isKYCVerified": getattr(user, 'is_kyc_verified', False),
                "createdAt": user.created_at.isoformat() if hasattr(user, 'created_at') and user.created_at else None
            }
            user_list.append(user_dict)
        
        return user_list
    except Exception as e:
        import traceback
        print(f"Error in get_all_users: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching users: {str(e)}"
        )


@router.post("/users/{user_id}/kyc/verify")
async def verify_user_kyc(
    user_id: str,
    current_user: User = Depends(get_current_admin)
):
    """Verify a user's KYC status"""
    try:
        user = await User.get(ObjectId(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_kyc_verified = True
        await user.save()
        
        return {
            "message": "User KYC verified successfully",
            "user_id": user_id,
            "user_name": f"{user.first_name} {user.last_name}"
        }
    
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )


@router.post("/users/{user_id}/kyc/reject")
async def reject_user_kyc(
    user_id: str,
    current_user: User = Depends(get_current_admin)
):
    """Reject a user's KYC status"""
    try:
        user = await User.get(ObjectId(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_kyc_verified = False
        await user.save()
        
        return {
            "message": "User KYC rejected successfully",
            "user_id": user_id,
            "user_name": f"{user.first_name} {user.last_name}"
        }
    
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )