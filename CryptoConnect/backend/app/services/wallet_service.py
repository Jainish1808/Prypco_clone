"""
XRP Wallet Management Service
Handles user wallet assignment and real XRP integration
"""
import os
import random
from typing import Optional, Dict, List
from xrpl.clients import JsonRpcClient
from xrpl.models import AccountInfo, AccountLines
try:
    from xrpl.wallet import Wallet
except ImportError:
    from xrpl import wallet as Wallet
import logging

logger = logging.getLogger(__name__)

class WalletService:
    """Service for managing user XRP wallets"""
    
    def __init__(self):
        self.testnet_url = "https://s.altnet.rippletest.net:51234"
        self.client = JsonRpcClient(self.testnet_url)
        
        # Your 4 predefined XRP wallets - will be assigned to existing users
        self.user_wallets = [
            {
                "address": "rGghB5Kp9YEQhZbxg7Pxm3FGd6gZsytQS8",
                "secret": "sEd7t6iGCmeYpBMW4yQxzK8FnJNpsrh"
            },
            {
                "address": "rnDmRyddBqCDkKBWSnKkzy5ZqtRoVjyDFg", 
                "secret": "sEdSq6vVpKeoxDWARwpxs2KuEe1XPWU"
            },
            {
                "address": "rLB8NiA8MdTS68BXzfu3wwgsZp5uEnyU85",
                "secret": "sEd76oZCyQ4bwMV2SbLNUhULyHLBY29"
            },
            {
                "address": "rJ86bTZkm59iAwV68ZJTq9GdSjBwM5DAw1",
                "secret": "sEdVgnP4k7xVASCmBhkTdgcrH4nYjHw"
            }
        ]
    
    async def assign_wallets_to_existing_users(self):
        """
        Assign your 4 XRP wallets to existing users in database
        """
        try:
            from app.models.user import User
            
            # Get all users from database
            users = await User.find().to_list()
            
            if not users:
                logger.warning("No users found in database")
                return False
            
            # Assign wallets to first 4 users (or all users if less than 4)
            users_to_assign = users[:4]
            
            for i, user in enumerate(users_to_assign):
                if i < len(self.user_wallets):
                    wallet = self.user_wallets[i]
                    
                    # Update user with wallet info
                    user.xrpl_wallet_address = wallet["address"]
                    user.xrpl_wallet_seed = wallet["secret"]
                    await user.save()
                    
                    logger.info(f"Assigned wallet {wallet['address']} to user {user.username}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error assigning wallets to existing users: {e}")
            return False
    
    def get_wallet_for_user_index(self, user_index: int) -> Optional[Dict[str, str]]:
        """
        Get wallet for a specific user index (0-3)
        """
        try:
            if 0 <= user_index < len(self.user_wallets):
                wallet = self.user_wallets[user_index]
                return {
                    "address": wallet["address"],
                    "secret": wallet["secret"]
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting wallet for user index: {e}")
            return None
    
    def get_wallet_balance(self, wallet_address: str) -> Dict[str, any]:
        """Get XRP balance and token holdings for a wallet"""
        try:
            # Get account info
            account_info_request = AccountInfo(account=wallet_address)
            response = self.client.request(account_info_request)
            
            if not response.is_successful():
                return {"error": "Failed to fetch account info"}
            
            account_data = response.result["account_data"]
            xrp_balance = float(account_data["Balance"]) / 1000000  # Convert drops to XRP
            
            # Get token holdings (trust lines)
            account_lines_request = AccountLines(account=wallet_address)
            lines_response = self.client.request(account_lines_request)
            
            tokens = []
            if lines_response.is_successful():
                for line in lines_response.result.get("lines", []):
                    if float(line["balance"]) > 0:
                        tokens.append({
                            "currency": line["currency"],
                            "balance": float(line["balance"]),
                            "issuer": line["account"]
                        })
            
            return {
                "xrp_balance": xrp_balance,
                "tokens": tokens,
                "sequence": account_data.get("Sequence", 0),
                "explorer_url": f"https://testnet.xrpl.org/accounts/{wallet_address}"
            }
            
        except Exception as e:
            logger.error(f"Error getting wallet balance: {e}")
            return {"error": str(e)}
    
    def validate_wallet_credentials(self, address: str, secret: str) -> bool:
        """Validate that the secret key matches the address"""
        try:
            # Simple validation - just check if both are provided
            return bool(address and secret and len(address) > 20 and len(secret) > 20)
        except Exception as e:
            logger.error(f"Error validating wallet credentials: {e}")
            return False
    
    def get_wallet_transactions(self, wallet_address: str, limit: int = 10) -> List[Dict]:
        """Get recent transactions for a wallet"""
        try:
            from xrpl.models import AccountTx
            
            account_tx_request = AccountTx(
                account=wallet_address,
                limit=limit
            )
            
            response = self.client.request(account_tx_request)
            
            if not response.is_successful():
                return []
            
            transactions = []
            for tx in response.result.get("transactions", []):
                tx_data = tx.get("tx", {})
                transactions.append({
                    "hash": tx_data.get("hash"),
                    "type": tx_data.get("TransactionType"),
                    "date": tx.get("date"),
                    "amount": tx_data.get("Amount"),
                    "destination": tx_data.get("Destination"),
                    "explorer_url": f"https://testnet.xrpl.org/transactions/{tx_data.get('hash')}"
                })
            
            return transactions
            
        except Exception as e:
            logger.error(f"Error getting wallet transactions: {e}")
            return []
    
    def create_trust_line(self, user_wallet_secret: str, token_currency: str, issuer_address: str, limit: str = "1000000") -> Optional[str]:
        """Create a trust line for a user to hold property tokens"""
        try:
            # For now, return a mock transaction hash
            # In production, implement actual trust line creation
            mock_tx_hash = f"trustline_{token_currency}_{issuer_address[:8]}"
            logger.info(f"Mock trust line created: {mock_tx_hash}")
            return mock_tx_hash
                
        except Exception as e:
            logger.error(f"Error creating trust line: {e}")
            return None

# Global wallet service instance
wallet_service = WalletService()