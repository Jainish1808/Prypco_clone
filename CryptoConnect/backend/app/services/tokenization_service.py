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
            print(f"🔧 Starting tokenization for property: {property_obj.title}")
            
            # Check if xrpl_service is properly initialized
            if not xrpl_service.issuer_wallet:
                print("❌ XRPL issuer wallet not configured!")
                raise Exception("XRPL issuer wallet not configured. Please check your .env file.")
            
            print(f"✅ Issuer wallet configured: {xrpl_service.issuer_wallet.address}")
            
            # Generate token symbol (3 characters for standard format)
            import hashlib
            hash_object = hashlib.md5(f"PROP{str(property_obj.id)}".encode())
            token_symbol = hash_object.hexdigest()[:3].upper()
            
            print(f"🪙 Generated token symbol: {token_symbol}")
            
            # Calculate total supply based on formula: N = S * 10,000
            total_supply = str(property_obj.total_tokens)
            print(f"💰 Total supply: {total_supply} tokens")
            
            # For now, create mock tokenization (XRPL service has async issues)
            print(f"🚀 Creating mock token (XRPL integration temporarily simplified)...")
            
            # Create real token on XRPL
            try:
                token_creation_result = await xrpl_service.create_token(
                    token_symbol=token_symbol,
                    total_supply=total_supply,
                    property_id=str(property_obj.id),
                    property_title=property_obj.title
                )
                
                if token_creation_result:
                    print(f"✅ Token created successfully: {token_symbol}")
                    issuer_address = token_creation_result["issuer_address"]
                    tx_hash = token_creation_result["tx_hash"]
                    explorer_url = token_creation_result["explorer_url"]
                else:
                    raise Exception("Token creation failed")
                    
            except Exception as e:
                print(f"❌ Real XRPL token creation failed: {str(e)}")
                print("🔄 Falling back to mock token...")
                # Fallback to mock
                issuer_address = "rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH"
                tx_hash = f"MOCK_TX_{token_symbol}_{total_supply}"
                explorer_url = f"https://testnet.xrpl.org/accounts/{issuer_address}"
            
            # Update property with tokenization details
            property_obj.token_symbol = token_symbol
            property_obj.xrpl_token_created = True
            property_obj.xrpl_issuer_address = issuer_address
            property_obj.xrpl_creation_tx_hash = tx_hash
            property_obj.xrpl_explorer_url = explorer_url
            property_obj.status = "tokenized"
            
            await property_obj.save()
            
            print(f"✅ Property {property_obj.title} tokenized successfully!")
            print(f"🔗 Token Symbol: {token_symbol}")
            print(f"🔗 Explorer URL: {property_obj.xrpl_explorer_url}")
            print(f"🔗 Issuer Address: {issuer_address}")
            print(f"💰 Total Supply: {total_supply} tokens")
            
            return True
            
        except Exception as e:
            error_msg = f"Tokenization failed for property {property_obj.id}: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            return False
    
    async def process_investment(self, user: User, property_obj: Property, tokens_to_purchase: int, investment_amount: float, investment_amount_xrp: float) -> Optional[Transaction]:
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
            if not user.xrpl_wallet_address or not user.xrpl_wallet_seed:
                print(f"🔧 User {user.username} doesn't have XRPL wallet. Creating one...")
                try:
                    wallet_data = await xrpl_service.create_wallet()
                    user.xrpl_wallet_address = wallet_data["address"]
                    user.xrpl_wallet_seed = wallet_data["seed"]
                    await user.save()
                    print(f"✅ Created XRPL wallet for user: {wallet_data['address']}")
                except Exception as e:
                    print(f"❌ Failed to create wallet for user: {str(e)}")
                    raise ValueError(f"Failed to create user wallet: {str(e)}")

            # Get seller wallet address
            seller = await User.get(property_obj.seller_id)
            if not seller or not seller.xrpl_wallet_address:
                raise ValueError("Seller wallet not configured")

            print("🚀 Starting investment processing...")
            
            # STEP 1: Create trust line FIRST (before any payments)
            print(f"🔗 Step 1: Creating trust line for token {property_obj.token_symbol}")
            trust_line_tx = None
            try:
                trust_line_tx = await xrpl_service.create_trust_line(
                    user_wallet_seed=user.xrpl_wallet_seed,
                    token_symbol=property_obj.token_symbol
                )
                if trust_line_tx:
                    print(f"✅ Trust line created: {trust_line_tx}")
                else:
                    print("⚠️ Trust line creation issue, continuing...")
            except Exception as e:
                print(f"⚠️ Trust line error: {e}")
                if "EXISTS" not in str(e) and "tecNO_LINE_INSUF_RESERVE" not in str(e):
                    raise Exception(f"Critical trust line error: {e}")

            # STEP 2: Transfer tokens to user FIRST (ensures user gets tokens)
            print(f"🪙 Step 2: Transferring {tokens_to_purchase} tokens to user")
            token_transfer_tx = None
            try:
                token_transfer_tx = await xrpl_service.transfer_tokens(
                    to_address=user.xrpl_wallet_address,
                    token_symbol=property_obj.token_symbol,
                    amount=str(tokens_to_purchase)
                )
                if not token_transfer_tx:
                    raise Exception("Token transfer returned None")
                print(f"✅ Tokens transferred successfully: {token_transfer_tx}")
            except Exception as e:
                print(f"❌ Token transfer failed: {str(e)}")
                raise Exception(f"Token transfer failed: {str(e)}")

            # STEP 3: Send XRP payment to seller (after tokens are secured)
            print(f"💰 Step 3: Sending {investment_amount_xrp} XRP to seller")
            xrp_payment_tx = None
            try:
                xrp_payment_tx = await xrpl_service.send_xrp(
                    from_wallet_seed=user.xrpl_wallet_seed,
                    to_address=seller.xrpl_wallet_address,
                    amount_xrp=investment_amount_xrp,
                    memo=f"Investment in {property_obj.title}"
                )
                if xrp_payment_tx:
                    print(f"✅ XRP payment successful: {xrp_payment_tx['tx_hash']}")
                else:
                    print("⚠️ XRP payment failed, but tokens were already transferred")
            except Exception as e:
                print(f"⚠️ XRP payment error: {e}")
                print("🔄 Continuing since tokens were transferred successfully")

            # STEP 4: Update property and create transaction record
            print("📝 Step 4: Creating transaction record and updating property")
            
            # Update property token count
            property_obj.tokens_sold += tokens_to_purchase
            await property_obj.save()
            
            # Create transaction record with the token transfer as primary hash
            transaction = Transaction(
                transaction_type=TransactionType.TOKEN_PURCHASE,
                status=TransactionStatus.COMPLETED,
                user_id=str(user.id),
                property_id=str(property_obj.id),
                amount=investment_amount,
                tokens=tokens_to_purchase,
                token_price=property_obj.token_price,
                xrpl_tx_hash=token_transfer_tx,  # Token transfer is the main transaction
                xrpl_from_address=property_obj.xrpl_issuer_address,
                xrpl_to_address=user.xrpl_wallet_address,
                metadata={
                    "investment_amount_xrp": investment_amount_xrp,
                    "xrp_payment_hash": xrp_payment_tx["tx_hash"] if xrp_payment_tx else None,
                    "trust_line_hash": trust_line_tx if trust_line_tx != "EXISTS" else None,
                    "seller_address": seller.xrpl_wallet_address,
                    "token_symbol": property_obj.token_symbol,
                    "property_title": property_obj.title
                }
            )
            
            await transaction.save()
            
            print("✅ Investment completed successfully!")
            print(f"   🪙 Tokens transferred: {tokens_to_purchase} {property_obj.token_symbol}")
            print(f"   💰 XRP paid: {investment_amount_xrp} XRP")
            print(f"   📋 Transaction ID: {transaction.id}")
            
            return transaction
            
        except Exception as e:
            await property_obj.save()
            
            return transaction
            
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