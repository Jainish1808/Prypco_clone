import xrpl
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import TrustSet, Payment
from xrpl.models.requests import AccountLines, AccountInfo
from xrpl.utils import xrp_to_drops, drops_to_xrp
from typing import Optional, Dict, Any
import asyncio
from app.config import settings


class XRPLService:
    def __init__(self):
        # Initialize XRPL client
        if settings.xrpl_network == "testnet":
            self.client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
        else:
            self.client = JsonRpcClient("https://xrplcluster.com/")
        
        # Initialize issuer wallet if provided
        self.issuer_wallet = None
        if settings.issuer_wallet_seed:
            self.issuer_wallet = Wallet.from_seed(settings.issuer_wallet_seed)
    
    async def create_wallet(self) -> Dict[str, str]:
        """Create a new XRPL wallet"""
        try:
            # Generate new wallet
            wallet = Wallet.create()
            
            # Fund wallet on testnet
            if settings.xrpl_network == "testnet":
                fund_result = await self._fund_wallet(wallet.address)
                if not fund_result:
                    raise Exception("Failed to fund wallet")
            
            return {
                "address": wallet.address,
                "seed": wallet.seed,
                "public_key": wallet.public_key,
                "private_key": wallet.private_key
            }
        except Exception as e:
            raise Exception(f"Failed to create wallet: {str(e)}")
    
    async def _fund_wallet(self, address: str) -> bool:
        """Fund a wallet on testnet using faucet API"""
        try:
            import httpx
            # Use testnet faucet API directly
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://faucet.altnet.rippletest.net/accounts",
                    json={"destination": address, "xrpAmount": "1000"}
                )
                return response.status_code == 200
        except Exception:
            return False
    
    async def create_trust_line(self, user_wallet_seed: str, token_symbol: str, issuer_address: str, limit: str = "1000000000") -> Optional[str]:
        """Create a trust line for a token"""
        try:
            user_wallet = Wallet.from_seed(user_wallet_seed)
            
            # Create trust line transaction
            trust_set = TrustSet(
                account=user_wallet.address,
                limit_amount={
                    "currency": token_symbol,
                    "issuer": issuer_address,
                    "value": limit
                }
            )
            
            # Submit and wait for validation
            response = xrpl.transaction.submit_and_wait(trust_set, self.client, user_wallet)
            
            if response.result["meta"]["TransactionResult"] == "tesSUCCESS":
                return response.result["hash"]
            else:
                raise Exception(f"Trust line creation failed: {response.result['meta']['TransactionResult']}")
                
        except Exception as e:
            raise Exception(f"Failed to create trust line: {str(e)}")
    
    async def create_token(self, token_symbol: str, total_supply: str) -> Optional[str]:
        """Create a new token (this is done by issuing to self first)"""
        try:
            if not self.issuer_wallet:
                raise Exception("Issuer wallet not configured")
            
            # Create payment to self to establish the token
            payment = Payment(
                account=self.issuer_wallet.address,
                destination=self.issuer_wallet.address,
                amount={
                    "currency": token_symbol,
                    "issuer": self.issuer_wallet.address,
                    "value": total_supply
                }
            )
            
            # Submit and wait for validation
            response = xrpl.transaction.submit_and_wait(payment, self.client, self.issuer_wallet)
            
            if response.result["meta"]["TransactionResult"] == "tesSUCCESS":
                return response.result["hash"]
            else:
                raise Exception(f"Token creation failed: {response.result['meta']['TransactionResult']}")
                
        except Exception as e:
            raise Exception(f"Failed to create token: {str(e)}")
    
    async def transfer_tokens(self, to_address: str, token_symbol: str, amount: str) -> Optional[str]:
        """Transfer tokens from issuer to user"""
        try:
            if not self.issuer_wallet:
                raise Exception("Issuer wallet not configured")
            
            # Create payment transaction
            payment = Payment(
                account=self.issuer_wallet.address,
                destination=to_address,
                amount={
                    "currency": token_symbol,
                    "issuer": self.issuer_wallet.address,
                    "value": amount
                }
            )
            
            # Submit and wait for validation
            response = xrpl.transaction.submit_and_wait(payment, self.client, self.issuer_wallet)
            
            if response.result["meta"]["TransactionResult"] == "tesSUCCESS":
                return response.result["hash"]
            else:
                raise Exception(f"Token transfer failed: {response.result['meta']['TransactionResult']}")
                
        except Exception as e:
            raise Exception(f"Failed to transfer tokens: {str(e)}")
    
    async def get_token_balance(self, address: str, token_symbol: str, issuer_address: str) -> float:
        """Get token balance for an address"""
        try:
            # Get account lines (trust lines)
            account_lines_request = AccountLines(
                account=address,
                ledger_index="validated"
            )
            
            response = self.client.request(account_lines_request)
            
            if response.is_successful():
                lines = response.result.get("lines", [])
                for line in lines:
                    if line["currency"] == token_symbol and line["account"] == issuer_address:
                        return float(line["balance"])
                return 0.0
            else:
                raise Exception("Failed to get account lines")
                
        except Exception as e:
            raise Exception(f"Failed to get token balance: {str(e)}")
    
    async def get_account_info(self, address: str) -> Optional[Dict[str, Any]]:
        """Get account information"""
        try:
            account_info_request = AccountInfo(
                account=address,
                ledger_index="validated"
            )
            
            response = self.client.request(account_info_request)
            
            if response.is_successful():
                return response.result["account_data"]
            else:
                return None
                
        except Exception as e:
            return None


# Global XRPL service instance
xrpl_service = XRPLService()