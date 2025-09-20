import xrpl
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import TrustSet, Payment, AccountSet
from xrpl.models.requests import AccountLines, AccountInfo, AccountObjects, Tx
from xrpl.utils import xrp_to_drops, drops_to_xrp
from typing import Optional, Dict, Any, List
import asyncio
import hashlib
import concurrent.futures
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
    
    async def _run_sync_xrpl_operation(self, operation_func, *args, **kwargs):
        """Run synchronous XRPL operations in thread pool to avoid blocking async context"""
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, operation_func, *args, **kwargs)
    
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
            
            # Submit and wait for validation using thread pool
            def submit_trust_line():
                return xrpl.transaction.submit_and_wait(trust_set, self.client, user_wallet)
            
            response = await self._run_sync_xrpl_operation(submit_trust_line)
            
            if response.result["meta"]["TransactionResult"] == "tesSUCCESS":
                return response.result["hash"]
            else:
                raise Exception(f"Trust line creation failed: {response.result['meta']['TransactionResult']}")
                
        except Exception as e:
            raise Exception(f"Failed to create trust line: {str(e)}")
    
    async def create_token(self, token_symbol: str, total_supply: str, property_id: str, property_title: str) -> Optional[Dict[str, str]]:
        """Create a new token and establish it on the XRPL"""
        try:
            print(f"🔧 Creating token: {token_symbol} with supply: {total_supply}")
            
            if not self.issuer_wallet:
                error_msg = "Issuer wallet not configured. Please set ISSUER_WALLET_SEED in your .env file."
                print(f"❌ {error_msg}")
                raise Exception(error_msg)
            
            print(f"✅ Using issuer wallet: {self.issuer_wallet.address}")
            
            # Ensure token symbol is properly formatted (3 chars for standard format)
            if len(token_symbol) != 3:
                # Create a 3-character token from property ID hash
                hash_object = hashlib.md5(f"PROP{property_id}".encode())
                token_symbol = hash_object.hexdigest()[:3].upper()
                print(f"🔄 Adjusted token symbol to: {token_symbol}")
            
            # Check client connection
            print("🌐 Testing XRPL connection...")
            try:
                from xrpl.models.requests import ServerInfo
                
                def test_connection():
                    return self.client.request(ServerInfo())
                
                server_info = await self._run_sync_xrpl_operation(test_connection)
                if not server_info.is_successful():
                    raise Exception("Failed to connect to XRPL server")
                print("✅ XRPL connection successful")
            except Exception as e:
                error_msg = f"XRPL connection failed: {str(e)}"
                print(f"❌ {error_msg}")
                raise Exception(error_msg)
            
            print("🚀 Creating token on XRPL...")
            
            # First, create a trust line from issuer to self (this establishes the token)
            self_trust_set = TrustSet(
                account=self.issuer_wallet.address,
                limit_amount={
                    "currency": token_symbol,
                    "issuer": self.issuer_wallet.address,
                    "value": "0"  # Self trust line with 0 limit
                }
            )
            
            # Submit self trust line
            print("📝 Creating self trust line...")
            
            def submit_self_trust():
                return xrpl.transaction.submit_and_wait(self_trust_set, self.client, self.issuer_wallet)
            
            self_trust_response = await self._run_sync_xrpl_operation(submit_self_trust)
            
            if self_trust_response.result["meta"]["TransactionResult"] != "tesSUCCESS":
                # If it fails due to tecNO_LINE_INSUF_RESERVE, that's actually OK - token already exists
                if self_trust_response.result["meta"]["TransactionResult"] != "tecNO_LINE_INSUF_RESERVE":
                    print(f"⚠️ Self trust line warning: {self_trust_response.result['meta']['TransactionResult']}")
            else:
                print("✅ Self trust line created successfully")
            
            # Now create the initial token supply by issuing to self
            print("💰 Issuing initial token supply...")
            issue_payment = Payment(
                account=self.issuer_wallet.address,
                destination=self.issuer_wallet.address,
                amount={
                    "currency": token_symbol,
                    "issuer": self.issuer_wallet.address,
                    "value": total_supply
                },
                memos=[{
                    "Memo": {
                        "MemoType": "50726F7065727479",  # "Property" in hex
                        "MemoData": f"{property_title} - Property Token".encode().hex(),
                        "MemoFormat": "746578742F706C61696E"  # "text/plain" in hex
                    }
                }]
            )
            
            # Submit and wait for validation using thread pool
            def submit_issue_payment():
                return xrpl.transaction.submit_and_wait(issue_payment, self.client, self.issuer_wallet)
            
            response = await self._run_sync_xrpl_operation(submit_issue_payment)
            
            if response.result["meta"]["TransactionResult"] == "tesSUCCESS":
                result = {
                    "tx_hash": response.result["hash"],
                    "token_symbol": token_symbol,
                    "issuer_address": self.issuer_wallet.address,
                    "total_supply": total_supply,
                    "ledger_index": str(response.result["ledger_index"]),
                    "explorer_url": f"https://testnet.xrpl.org/transactions/{response.result['hash']}"
                }
                print(f"✅ Token created successfully!")
                print(f"   TX Hash: {result['tx_hash']}")
                print(f"   Explorer: {result['explorer_url']}")
                return result
            else:
                error_msg = f"Token creation failed: {response.result['meta']['TransactionResult']}"
                print(f"❌ {error_msg}")
                raise Exception(error_msg)
                
        except Exception as e:
            error_msg = f"Failed to create token: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            raise Exception(error_msg)
    
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
            
            # Submit and wait for validation using thread pool
            def submit_payment():
                return xrpl.transaction.submit_and_wait(payment, self.client, self.issuer_wallet)
            
            response = await self._run_sync_xrpl_operation(submit_payment)
            
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
            
            def get_account_lines():
                return self.client.request(account_lines_request)
            
            response = await self._run_sync_xrpl_operation(get_account_lines)
            
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
    
    async def transfer_tokens_user_to_user(self, from_wallet_seed: str, to_address: str, token_symbol: str, issuer_address: str, amount: str, memo: str = None) -> Optional[Dict[str, str]]:
        """Transfer tokens between users (not from issuer)"""
        try:
            from_wallet = Wallet.from_seed(from_wallet_seed)
            
            # Create payment transaction
            payment = Payment(
                account=from_wallet.address,
                destination=to_address,
                amount={
                    "currency": token_symbol,
                    "issuer": issuer_address,
                    "value": amount
                }
            )
            
            # Add memo if provided
            if memo:
                payment.memos = [{
                    "Memo": {
                        "MemoType": "5472616E73666572",  # "Transfer" in hex
                        "MemoData": memo.encode().hex(),
                        "MemoFormat": "746578742F706C61696E"  # "text/plain" in hex
                    }
                }]
            
            # Submit and wait for validation using thread pool
            def submit_user_payment():
                return xrpl.transaction.submit_and_wait(payment, self.client, from_wallet)
            
            response = await self._run_sync_xrpl_operation(submit_user_payment)
            
            if response.result["meta"]["TransactionResult"] == "tesSUCCESS":
                return {
                    "tx_hash": response.result["hash"],
                    "from_address": from_wallet.address,
                    "to_address": to_address,
                    "amount": amount,
                    "token_symbol": token_symbol,
                    "ledger_index": str(response.result["ledger_index"]),
                    "explorer_url": f"https://testnet.xrpl.org/transactions/{response.result['hash']}"
                }
            else:
                raise Exception(f"Token transfer failed: {response.result['meta']['TransactionResult']}")
                
        except Exception as e:
            raise Exception(f"Failed to transfer tokens: {str(e)}")

    async def get_transaction_details(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """Get detailed transaction information"""
        try:
            tx_request = Tx(transaction=tx_hash)
            response = self.client.request(tx_request)
            
            if response.is_successful():
                return {
                    "transaction": response.result,
                    "explorer_url": f"https://testnet.xrpl.org/transactions/{tx_hash}",
                    "validated": response.result.get("validated", False)
                }
            else:
                return None
                
        except Exception as e:
            return None

    async def get_all_user_tokens(self, address: str) -> List[Dict[str, Any]]:
        """Get all tokens held by a user"""
        try:
            account_lines_request = AccountLines(
                account=address,
                ledger_index="validated"
            )
            
            response = self.client.request(account_lines_request)
            
            if response.is_successful():
                lines = response.result.get("lines", [])
                tokens = []
                for line in lines:
                    if float(line["balance"]) > 0:  # Only show tokens with positive balance
                        tokens.append({
                            "currency": line["currency"],
                            "issuer": line["account"],
                            "balance": float(line["balance"]),
                            "limit": line["limit"],
                            "quality_in": line.get("quality_in", 0),
                            "quality_out": line.get("quality_out", 0)
                        })
                return tokens
            else:
                return []
                
        except Exception as e:
            return []

    async def verify_token_on_ledger(self, token_symbol: str, issuer_address: str) -> Optional[Dict[str, Any]]:
        """Verify if a token exists on the XRPL and get its details"""
        try:
            # Get issuer account info to verify it exists
            issuer_info = await self.get_account_info(issuer_address)
            if not issuer_info:
                return None
            
            # Get account objects to find token-related objects
            account_objects_request = AccountObjects(
                account=issuer_address,
                ledger_index="validated"
            )
            
            response = self.client.request(account_objects_request)
            
            if response.is_successful():
                objects = response.result.get("account_objects", [])
                
                # Look for RippleState objects (trust lines) related to our token
                token_info = {
                    "token_symbol": token_symbol,
                    "issuer_address": issuer_address,
                    "exists": False,
                    "total_supply": "0",
                    "holders": []
                }
                
                # Check if we can find any trust lines for this token
                lines_request = AccountLines(
                    account=issuer_address,
                    ledger_index="validated"
                )
                
                lines_response = self.client.request(lines_request)
                if lines_response.is_successful():
                    lines = lines_response.result.get("lines", [])
                    for line in lines:
                        if line.get("currency") == token_symbol:
                            token_info["exists"] = True
                            if float(line["balance"]) < 0:  # Negative balance means tokens were issued
                                token_info["total_supply"] = str(abs(float(line["balance"])))
                            token_info["holders"].append({
                                "address": line["account"],
                                "balance": abs(float(line["balance"]))
                            })
                
                return token_info
            else:
                return None
                
        except Exception as e:
            return None

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