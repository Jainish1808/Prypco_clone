#!/usr/bin/env python3
"""
Debug script for XRPL tokenization issues
"""
import sys
import os
import asyncio

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.config import settings
from app.services.xrpl_service import XRPLService

async def debug_xrpl():
    """Debug XRPL service configuration"""
    print("🔍 Debugging XRPL Configuration")
    print("=" * 50)
    
    # Check configuration
    print(f"XRPL Network: {settings.xrpl_network}")
    print(f"Issuer Wallet Seed: {'SET' if settings.issuer_wallet_seed else 'NOT SET'}")
    print(f"Issuer Wallet Address: {'SET' if settings.issuer_wallet_address else 'NOT SET'}")
    
    if settings.issuer_wallet_seed:
        print(f"Seed starts with: {settings.issuer_wallet_seed[:10]}...")
    
    # Initialize XRPL service
    try:
        xrpl_service = XRPLService()
        print("\n✅ XRPL Service initialized successfully")
        
        # Check issuer wallet
        if xrpl_service.issuer_wallet:
            print(f"✅ Issuer wallet loaded: {xrpl_service.issuer_wallet.address}")
        else:
            print("❌ Issuer wallet not loaded!")
            
        # Test token creation
        print("\n🔧 Testing token creation...")
        test_result = await xrpl_service.create_token(
            token_symbol="TST",
            total_supply="1000000",
            property_id="test123",
            property_title="Test Property"
        )
        
        if test_result:
            print("✅ Token creation test successful!")
            print(f"   Token Symbol: {test_result['token_symbol']}")
            print(f"   Issuer: {test_result['issuer_address']}")
            print(f"   TX Hash: {test_result['tx_hash']}")
            print(f"   Explorer: {test_result['explorer_url']}")
        else:
            print("❌ Token creation test failed")
            
    except Exception as e:
        print(f"❌ Error initializing XRPL service: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_xrpl())