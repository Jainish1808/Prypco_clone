from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from datetime import datetime
from app.models.property import Property, PropertyCreate, PropertyResponse, PropertyUpdateSeller
from app.models.user import User
from app.auth import get_current_active_user, get_current_user
from app.services.tokenization_service import tokenization_service
from pydantic import BaseModel
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/seller", tags=["seller"])


@router.post("/test")
async def test_endpoint(data: dict):
    """Test endpoint to check if seller router is working"""
    logger.info(f"Test endpoint received data: {data}")
    return {"message": "Seller router is working", "received_data": data}


class PropertyCreateWithImages(PropertyCreate):
    images: Optional[List[str]] = []


@router.post("/property/submit", response_model=PropertyResponse)
async def submit_property(
    property_data: PropertyCreateWithImages,
    current_user: User = Depends(get_current_user)
):
    """Submit a new property for review"""
    try:
        logger.info(f"Property submission received from user {current_user.id}: {property_data.title}")
        logger.info(f"Property data: {property_data.dict()}")
        
        # Validate required fields
        if not property_data.title or not property_data.address:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title and address are required"
            )
        
        if property_data.total_value <= 0 or property_data.size_sqm <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Total value and size must be positive numbers"
            )
        
        # Create property object with current user as seller
        property_obj = Property(
            title=property_data.title,
            description=property_data.description or "Property description to be updated",
            address=property_data.address,
            city=property_data.city,
            country=property_data.country,
            property_type=property_data.property_type,
            total_value=property_data.total_value,
            size_sqm=property_data.size_sqm,
            bedrooms=property_data.bedrooms,
            bathrooms=property_data.bathrooms,
            parking_spaces=property_data.parking_spaces,
            year_built=property_data.year_built,
            monthly_rent=property_data.monthly_rent,
            seller_id=str(current_user.id),
            seller_name=f"{current_user.first_name or ''} {current_user.last_name or ''}".strip() or current_user.username,
            seller_email=current_user.email,
            images=property_data.images or []
        )
        
        # Calculate tokens and price using the formulas
        property_obj.calculate_tokens_and_price()
        logger.info(f"Calculated tokens: {property_obj.total_tokens}, price: {property_obj.token_price}")
        
        # Calculate annual yield if monthly rent is provided
        if property_data.monthly_rent and property_data.total_value > 0:
            annual_rent = property_data.monthly_rent * 12
            property_obj.annual_yield = (annual_rent / property_data.total_value) * 100
            logger.info(f"Calculated annual yield: {property_obj.annual_yield}%")
        
        await property_obj.save()
        
        logger.info(f"Property {property_obj.id} saved successfully")

        # Tokenize the property
        logger.info(f"Starting tokenization for property {property_obj.id}")
        tokenization_success = await tokenization_service.tokenize_property(property_obj)
        if tokenization_success:
            logger.info(f"Property {property_obj.id} tokenized successfully")
            
            # Refresh the property object to get updated tokenization details
            property_obj = await Property.get(property_obj.id)
            
            # Log the tokenization success with explorer links
            if property_obj.xrpl_explorer_url:
                logger.info(f"🚀 TOKENIZATION SUCCESSFUL!")
                logger.info(f"📍 Property: {property_obj.title}")
                logger.info(f"🪙 Token Symbol: {property_obj.token_symbol}")
                logger.info(f"💰 Total Supply: {property_obj.total_tokens} tokens")
                logger.info(f"💲 Token Price: {property_obj.token_price:.6f} AED per token")
                logger.info(f"🔗 XRP Testnet Explorer: {property_obj.xrpl_explorer_url}")
                logger.info(f"🏦 Issuer Address: {property_obj.xrpl_issuer_address}")
                logger.info(f"📊 View on XRPL Explorer: https://testnet.xrpl.org/accounts/{property_obj.xrpl_issuer_address}")
        else:
            logger.error(f"Property {property_obj.id} tokenization failed")
            # You might want to handle this failure case, e.g., by updating the property status
        
        response = PropertyResponse(
            id=str(property_obj.id),
            title=property_obj.title,
            description=property_obj.description,
            address=property_obj.address,
            city=property_obj.city,
            country=property_obj.country,
            property_type=property_obj.property_type,
            total_value=property_obj.total_value,
            size_sqm=property_obj.size_sqm,
            total_tokens=property_obj.total_tokens,
            token_price=property_obj.token_price,
            tokens_sold=property_obj.tokens_sold,
            bedrooms=property_obj.bedrooms,
            bathrooms=property_obj.bathrooms,
            parking_spaces=property_obj.parking_spaces,
            year_built=property_obj.year_built,
            monthly_rent=property_obj.monthly_rent,
            annual_yield=property_obj.annual_yield,
            seller_name=property_obj.seller_name,
            status=property_obj.status,
            images=property_obj.images,
            created_at=property_obj.created_at
        )
        
        logger.info(f"Returning response for property {response.id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting property: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit property: {str(e)}"
        )


@router.get("/property/{property_id}/tokenization")
async def get_property_tokenization_details(
    property_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get detailed tokenization information for a property"""
    try:
        logger.info(f"Fetching tokenization details for property {property_id}")
        
        property_obj = await Property.get(property_id)
        if not property_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found"
            )
        
        # Check if user is the seller
        if property_obj.seller_id != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view tokenization details for your own properties"
            )
        
        tokenization_details = {
            "property_id": str(property_obj.id),
            "title": property_obj.title,
            "status": property_obj.status,
            "tokenized": property_obj.xrpl_token_created,
            "token_details": {}
        }
        
        if property_obj.xrpl_token_created:
            tokenization_details["token_details"] = {
                "token_symbol": property_obj.token_symbol,
                "total_tokens": property_obj.total_tokens,
                "token_price": property_obj.token_price,
                "tokens_sold": property_obj.tokens_sold,
                "tokens_available": property_obj.total_tokens - property_obj.tokens_sold,
                "xrpl_details": {
                    "issuer_address": property_obj.xrpl_issuer_address,
                    "creation_tx_hash": property_obj.xrpl_creation_tx_hash,
                    "explorer_url": property_obj.xrpl_explorer_url,
                    "issuer_explorer_url": f"https://testnet.xrpl.org/accounts/{property_obj.xrpl_issuer_address}",
                    "network": "XRP Testnet"
                }
            }
            
            # Try to get live token information from XRP Ledger
            try:
                from app.services.xrpl_service import xrpl_service
                token_verification = await xrpl_service.verify_token_on_ledger(
                    property_obj.token_symbol,
                    property_obj.xrpl_issuer_address
                )
                
                if token_verification:
                    tokenization_details["token_details"]["live_data"] = {
                        "verified_on_ledger": token_verification.get("exists", False),
                        "live_total_supply": token_verification.get("total_supply", "0"),
                        "current_holders": len(token_verification.get("holders", [])),
                        "holder_details": token_verification.get("holders", [])
                    }
                    
            except Exception as e:
                logger.warning(f"Could not fetch live token data: {str(e)}")
                tokenization_details["token_details"]["live_data"] = {
                    "error": "Unable to fetch live data from XRP Ledger"
                }
        
        return tokenization_details
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tokenization details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tokenization details: {str(e)}"
        )


@router.post("/property/{property_id}/retokenize")
async def retokenize_property(
    property_id: str,
    current_user: User = Depends(get_current_user)
):
    """Retry tokenization for a property that failed"""
    try:
        logger.info(f"Retrying tokenization for property {property_id}")
        
        property_obj = await Property.get(property_id)
        if not property_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found"
            )
        
        # Check if user is the seller
        if property_obj.seller_id != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only retokenize your own properties"
            )
        
        # Check if already tokenized
        if property_obj.xrpl_token_created:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Property is already tokenized"
            )
        
        # Retry tokenization
        tokenization_success = await tokenization_service.tokenize_property(property_obj)
        
        if tokenization_success:
            # Refresh the property object
            property_obj = await Property.get(property_obj.id)
            
            return {
                "success": True,
                "message": "Property tokenized successfully",
                "token_symbol": property_obj.token_symbol,
                "explorer_url": property_obj.xrpl_explorer_url,
                "issuer_address": property_obj.xrpl_issuer_address
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Tokenization failed. Please try again later."
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retokenizing property: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retokenize property: {str(e)}"
        )
    """Debug endpoint to get all properties without authentication"""
    try:
        logger.info("Fetching all properties for debug")
        properties = await Property.find().to_list()
        logger.info(f"Found {len(properties)} total properties")
        
        return [
            {
                "id": str(prop.id),
                "title": prop.title,
                "seller_id": prop.seller_id,
                "seller_name": prop.seller_name,
                "status": prop.status,
                "total_value": prop.total_value,
                "size_sqm": prop.size_sqm,
                "total_tokens": prop.total_tokens,
                "token_price": prop.token_price,
                "created_at": prop.created_at.isoformat()
            }
            for prop in properties
        ]
    except Exception as e:
        logger.error(f"Error fetching properties for debug: {e}")
        return {"error": str(e)}


@router.get("/properties", response_model=List[PropertyResponse])
async def get_seller_properties(current_user: User = Depends(get_current_user)):
    """Get all properties submitted by the current seller"""
    try:
        logger.info(f"Fetching properties for seller {current_user.id}")
        logger.info(f"User role: {current_user.role}")
        logger.info(f"User active: {current_user.is_active}")
        
        properties = await Property.find(Property.seller_id == str(current_user.id)).to_list()
        logger.info(f"Found {len(properties)} properties for seller {current_user.id}")
        
        # If no properties found, let's check if there are any properties at all
        if len(properties) == 0:
            all_properties = await Property.find().to_list()
            logger.info(f"Total properties in database: {len(all_properties)}")
            for prop in all_properties:
                logger.info(f"Property {prop.id}: seller_id={prop.seller_id}, current_user_id={str(current_user.id)}")
        
    except Exception as e:
        logger.error(f"Error fetching seller properties: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch properties: {str(e)}"
        )
    
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


@router.get("/property/{property_id}", response_model=PropertyResponse)
async def get_seller_property(
    property_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific property submitted by the seller"""
    try:
        property_obj = await Property.get(property_id)
        if not property_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found"
            )
        
        # Check if the property belongs to the current seller (or if user is admin)
        from app.models.user import UserRole
        if property_obj.seller_id != str(current_user.id) and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this property"
            )
        
        return PropertyResponse(
            id=str(property_obj.id),
            title=property_obj.title,
            description=property_obj.description,
            address=property_obj.address,
            city=property_obj.city,
            country=property_obj.country,
            property_type=property_obj.property_type,
            total_value=property_obj.total_value,
            size_sqm=property_obj.size_sqm,
            total_tokens=property_obj.total_tokens,
            token_price=property_obj.token_price,
            tokens_sold=property_obj.tokens_sold,
            bedrooms=property_obj.bedrooms,
            bathrooms=property_obj.bathrooms,
            parking_spaces=property_obj.parking_spaces,
            year_built=property_obj.year_built,
            monthly_rent=property_obj.monthly_rent,
            annual_yield=property_obj.annual_yield,
            seller_name=property_obj.seller_name,
            status=property_obj.status,
            images=property_obj.images,
            created_at=property_obj.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching property {property_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch property: {str(e)}"
        )


@router.put("/property/{property_id}", response_model=PropertyResponse)
async def update_seller_property(
    property_id: str,
    property_update: PropertyUpdateSeller,
    current_user: User = Depends(get_current_user)
):
    """Update a property (only allowed for pending review properties)"""
    try:
        property_obj = await Property.get(property_id)
        if not property_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found"
            )
        
        # Check if the property belongs to the current seller
        if property_obj.seller_id != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to edit this property"
            )
        
        # Only allow editing properties that are pending review
        from app.models.property import PropertyStatus
        if property_obj.status != PropertyStatus.PENDING_REVIEW:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only edit properties that are pending review"
            )
        
        # Update fields that are provided
        update_data = property_update.dict(exclude_unset=True)
        
        # If financial fields are updated, recalculate tokens and price
        recalculate_needed = False
        
        for field, value in update_data.items():
            if field == "images":
                property_obj.images = value or []
            elif hasattr(property_obj, field):
                setattr(property_obj, field, value)
                if field in ['total_value', 'size_sqm']:
                    recalculate_needed = True
        
        # Recalculate tokens and price if needed
        if recalculate_needed:
            property_obj.calculate_tokens_and_price()
            logger.info(f"Recalculated tokens: {property_obj.total_tokens}, price: {property_obj.token_price}")
        
        # Recalculate annual yield if monthly rent or total value changed
        if 'monthly_rent' in update_data or 'total_value' in update_data:
            if property_obj.monthly_rent and property_obj.total_value > 0:
                annual_rent = property_obj.monthly_rent * 12
                property_obj.annual_yield = (annual_rent / property_obj.total_value) * 100
            else:
                property_obj.annual_yield = None
        
        # Update timestamp
        property_obj.updated_at = datetime.utcnow()
        
        await property_obj.save()
        
        logger.info(f"Property {property_obj.id} updated successfully by seller {current_user.id}")
        
        return PropertyResponse(
            id=str(property_obj.id),
            title=property_obj.title,
            description=property_obj.description,
            address=property_obj.address,
            city=property_obj.city,
            country=property_obj.country,
            property_type=property_obj.property_type,
            total_value=property_obj.total_value,
            size_sqm=property_obj.size_sqm,
            total_tokens=property_obj.total_tokens,
            token_price=property_obj.token_price,
            tokens_sold=property_obj.tokens_sold,
            bedrooms=property_obj.bedrooms,
            bathrooms=property_obj.bathrooms,
            parking_spaces=property_obj.parking_spaces,
            year_built=property_obj.year_built,
            monthly_rent=property_obj.monthly_rent,
            annual_yield=property_obj.annual_yield,
            seller_name=property_obj.seller_name,
            status=property_obj.status,
            images=property_obj.images,
            created_at=property_obj.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating property {property_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update property: {str(e)}"
        )