from typing import Optional
from app.models.property import Property
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.models.user import User
from app.services.xrpl_service import xrpl_service
import asyncio


class TokenizationService:
    
    async def tokenize_property(self, property_obj: Property) -> bool:
        """Tokenize a property by creating tokens on XRPL"""
        try:
            # Generate token symbol (e.g., PROP001)
            token_symbol = f"PROP{str(property_obj.id)[-6:].upper()}"
            
            # Calculate total supply based on formula: N = S * 10,000
            total_supply = str(property_obj.total_tokens)
            
            # Create token on XRPL
            tx_hash = await xrpl_service.create_token(token_symbol, total_supply)
            
            if tx_hash:
                # Update property with tokenization details
                property_obj.token_symbol = token_symbol
                property_obj.xrpl_token_created = True
                property_obj.xrpl_issuer_address = xrpl_service.issuer_wallet.address if xrpl_service.issuer_wallet else None
                property_obj.xrpl_creation_tx_hash = tx_hash
                property_obj.status = "tokenized"
                
                await property_obj.save()
                return True
            
            return False
            
        except Exception as e:
            print(f"Tokenization failed for property {property_obj.id}: {str(e)}")
            return False
    
    async def process_investment(self, user: User, property_obj: Property, tokens_to_purchase: int, investment_amount: float) -> Optional[Transaction]:
        """Process an investment by transferring tokens to user"""
        try:
            # Validate investment
            if tokens_to_purchase <= 0:
                raise ValueError("Invalid token amount")
            
            if property_obj.tokens_sold + tokens_to_purchase > property_obj.total_tokens:
                raise ValueError("Not enough tokens available")
            
            if not property_obj.xrpl_token_created:
                raise ValueError("Property not tokenized yet")
            
            # Ensure user has XRPL wallet
            if not user.xrpl_wallet_address:
                wallet_info = await xrpl_service.create_wallet()
                user.xrpl_wallet_address = wallet_info["address"]
                user.xrpl_wallet_seed = wallet_info["seed"]  # In production, encrypt this
                await user.save()
            
            # Create trust line if needed
            trust_line_tx = await xrpl_service.create_trust_line(
                user.xrpl_wallet_seed,
                property_obj.token_symbol,
                property_obj.xrpl_issuer_address
            )
            
            # Transfer tokens to user
            transfer_tx = await xrpl_service.transfer_tokens(
                user.xrpl_wallet_address,
                property_obj.token_symbol,
                str(tokens_to_purchase)
            )
            
            if transfer_tx:
                # Create transaction record
                transaction = Transaction(
                    transaction_type=TransactionType.TOKEN_PURCHASE,
                    status=TransactionStatus.COMPLETED,
                    user_id=str(user.id),
                    property_id=str(property_obj.id),
                    amount=investment_amount,
                    tokens=tokens_to_purchase,
                    token_price=property_obj.token_price,
                    xrpl_tx_hash=transfer_tx,
                    xrpl_from_address=property_obj.xrpl_issuer_address,
                    xrpl_to_address=user.xrpl_wallet_address
                )
                
                await transaction.save()
                
                # Update property tokens sold
                property_obj.tokens_sold += tokens_to_purchase
                if property_obj.tokens_sold >= property_obj.total_tokens:
                    property_obj.status = "sold_out"
                
                await property_obj.save()
                
                return transaction
            
            return None
            
        except Exception as e:
            print(f"Investment processing failed: {str(e)}")
            # Create failed transaction record
            transaction = Transaction(
                transaction_type=TransactionType.TOKEN_PURCHASE,
                status=TransactionStatus.FAILED,
                user_id=str(user.id),
                property_id=str(property_obj.id),
                amount=investment_amount,
                tokens=tokens_to_purchase,
                token_price=property_obj.token_price,
                notes=str(e)
            )
            await transaction.save()
            return None
    
    async def calculate_ownership_fraction(self, tokens_owned: int, total_tokens: int) -> float:
        """Calculate ownership fraction: F = k / N"""
        if total_tokens == 0:
            return 0.0
        return tokens_owned / total_tokens
    
    async def calculate_rental_income_share(self, tokens_owned: int, total_tokens: int, total_rental_income: float) -> float:
        """Calculate rental income share: I = (k / N) * R"""
        ownership_fraction = await self.calculate_ownership_fraction(tokens_owned, total_tokens)
        return ownership_fraction * total_rental_income
    
    async def distribute_rental_income(self, property_obj: Property, total_rental_income: float) -> bool:
        """Distribute rental income to all token holders"""
        try:
            # Get all transactions for this property to find token holders
            transactions = await Transaction.find(
                Transaction.property_id == str(property_obj.id),
                Transaction.transaction_type == TransactionType.TOKEN_PURCHASE,
                Transaction.status == TransactionStatus.COMPLETED
            ).to_list()
            
            # Calculate holdings per user
            user_holdings = {}
            for tx in transactions:
                if tx.user_id not in user_holdings:
                    user_holdings[tx.user_id] = 0
                user_holdings[tx.user_id] += tx.tokens
            
            # Distribute income
            for user_id, tokens_owned in user_holdings.items():
                income_share = await self.calculate_rental_income_share(
                    tokens_owned, property_obj.total_tokens, total_rental_income
                )
                
                # Create income distribution transaction
                distribution_tx = Transaction(
                    transaction_type=TransactionType.RENTAL_DISTRIBUTION,
                    status=TransactionStatus.COMPLETED,
                    user_id=user_id,
                    property_id=str(property_obj.id),
                    amount=income_share,
                    tokens=tokens_owned,
                    token_price=0,  # Not applicable for distributions
                    metadata={
                        "total_rental_income": total_rental_income,
                        "ownership_percentage": (tokens_owned / property_obj.total_tokens) * 100
                    }
                )
                
                await distribution_tx.save()
            
            return True
            
        except Exception as e:
            print(f"Rental income distribution failed: {str(e)}")
            return False


# Global tokenization service instance
tokenization_service = TokenizationService()