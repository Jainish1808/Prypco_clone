from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.models.property import Property, PropertyCreate, PropertyResponse, InvestmentRequest, PropertyStatus
from app.models.user import User
from app.auth import get_current_verified_user, get_current_active_user, get_current_investor
from app.services.tokenization_service import tokenization_service

router = APIRouter(prefix="/api", tags=["properties"])


@router.get("/properties", response_model=List[PropertyResponse])
async def get_properties():
    """Get all approved properties for investors"""
    try:
        # Get all properties first
        all_properties = await Property.find().to_list()
        print(f"Total properties found: {len(all_properties)}")
        
        # Filter properties manually to handle enum status values
        approved_properties = []
        for prop in all_properties:
            status_str = str(prop.status).lower()
            print(f"Property: {prop.title}, Status: {prop.status}, Status String: {status_str}")
            
            # Check if status contains any of the approved states
            if any(approved_status in status_str for approved_status in ["approved", "tokenized", "sold_out"]):
                approved_properties.append(prop)
        
        print(f"Approved properties found: {len(approved_properties)}")
        properties = approved_properties
        
    except Exception as e:
        # If there's any error, return empty list
        print(f"Error fetching properties: {e}")
        return []
    
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


@router.get("/properties/{property_id}", response_model=PropertyResponse)
async def get_property(property_id: str):
    """Get detailed information about a specific property"""
    try:
        from bson import ObjectId
        # Try to get by ObjectId first, then by string ID
        if ObjectId.is_valid(property_id):
            property_obj = await Property.get(ObjectId(property_id))
        else:
            property_obj = await Property.get(property_id)
            
        if not property_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Property not found: {str(e)}"
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


@router.post("/properties/{property_id}/invest")
async def invest_in_property(
    property_id: str,
    investment_data: InvestmentRequest,
    current_user: User = Depends(get_current_investor)
):
    """Invest in a property by purchasing tokens - INVESTOR ACCESS ONLY"""
    # Get property
    property_obj = await Property.get(property_id)
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Check if property is available for investment
    if property_obj.status not in ["approved", "tokenized"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Property not available for investment"
        )
    
    # Validate investment amount and tokens
    expected_amount = investment_data.tokens_to_purchase * property_obj.token_price
    if abs(investment_data.investment_amount - expected_amount) > 0.01:  # Allow small rounding differences
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Investment amount doesn't match token price calculation"
        )
    
    # Check token availability
    if property_obj.tokens_sold + investment_data.tokens_to_purchase > property_obj.total_tokens:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough tokens available"
        )
    
    # Tokenize property if not already done
    if not property_obj.xrpl_token_created:
        tokenization_success = await tokenization_service.tokenize_property(property_obj)
        if not tokenization_success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to tokenize property"
            )
    
    # Process investment
    transaction = await tokenization_service.process_investment(
        current_user,
        property_obj,
        investment_data.tokens_to_purchase,
        investment_data.investment_amount,
        investment_data.investment_amount_xrp
    )
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process investment"
        )
    
    return {
        "message": "Investment successful",
        "transaction_id": str(transaction.id),
        "tokens_purchased": investment_data.tokens_to_purchase,
        "amount_invested": investment_data.investment_amount,
        "xrpl_tx_hash": transaction.xrpl_tx_hash
    }