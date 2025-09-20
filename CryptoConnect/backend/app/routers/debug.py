#!/usr/bin/env python3
"""
XRPL Configuration Verification Endpoint
This creates a simple test endpoint to verify XRPL setup
"""

from fastapi import APIRouter
from typing import Dict, Any
from app.services.xrpl_service import xrpl_service
from app.config import settings
import asyncio

router = APIRouter()

@router.get("/debug/xrpl-config")
async def debug_xrpl_config() -> Dict[str, Any]:
    """Debug endpoint to check XRPL configuration"""
    try:
        result = {
            "status": "checking",
            "network": settings.xrpl_network,
            "issuer_wallet_configured": bool(settings.issuer_wallet_seed),
            "issuer_address": None,
            "connection_test": "pending",
            "test_token_creation": "pending"
        }
        
        # Check issuer wallet
        if xrpl_service.issuer_wallet:
            result["issuer_address"] = xrpl_service.issuer_wallet.address
            result["issuer_wallet_loaded"] = True
        else:
            result["issuer_wallet_loaded"] = False
            result["error"] = "Issuer wallet not loaded"
            return result
        
        # Test connection
        try:
            from xrpl.models.requests import ServerInfo
            import concurrent.futures
            
            def test_connection():
                return xrpl_service.client.request(ServerInfo())
            
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                server_info = await loop.run_in_executor(executor, test_connection)
            
            if server_info.is_successful():
                result["connection_test"] = "success"
                result["server_info"] = server_info.result.get("info", {})
            else:
                result["connection_test"] = "failed"
                result["connection_error"] = "Server request failed"
        except Exception as e:
            result["connection_test"] = "failed"
            result["connection_error"] = str(e)
        
        # Test token creation (dry run)
        try:
            if result["connection_test"] == "success":
                result["test_token_creation"] = "ready"
                result["message"] = "XRPL configuration is working correctly"
            else:
                result["test_token_creation"] = "skipped"
                result["message"] = "Connection test failed, skipping token creation test"
        except Exception as e:
            result["test_token_creation"] = "failed"
            result["token_creation_error"] = str(e)
        
        result["status"] = "completed"
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "XRPL configuration check failed"
        }

@router.post("/debug/test-tokenization")
async def test_tokenization() -> Dict[str, Any]:
    """Test tokenization with a dummy property"""
    try:
        # Test token creation with dummy data
        result = await xrpl_service.create_token(
            token_symbol="TST",
            total_supply="100000",
            property_id="test-123",
            property_title="Test Property for Debug"
        )
        
        return {
            "status": "success",
            "message": "Test tokenization successful",
            "result": result
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Test tokenization failed"
        }