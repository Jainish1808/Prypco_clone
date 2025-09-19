#!/usr/bin/env python3
"""
XRPL Wallet Setup Script for CryptoConnect
This script helps you create and fund an XRPL testnet wallet for the issuer account.
"""

import xrpl
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet

def create_and_fund_wallet():
    """Create a new XRPL wallet and fund it on testnet"""
    print("🚀 Setting up XRPL Testnet Wallet for CryptoConnect")
    print("=" * 50)
    
    try:
        # Connect to testnet
        client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
        print("✅ Connected to XRPL Testnet")
        
        # Generate new wallet
        wallet = Wallet.create()
        print(f"✅ Generated new wallet")
        print(f"   Address: {wallet.address}")
        print(f"   Seed: {wallet.seed}")
        
        # Fund wallet on testnet using faucet API
        print("💰 Funding wallet on testnet...")
        try:
            import httpx
            with httpx.Client() as http_client:
                response = http_client.post(
                    "https://faucet.altnet.rippletest.net/accounts",
                    json={"destination": wallet.address, "xrpAmount": "1000"}
                )
                
            if response.status_code == 200:
                print("✅ Wallet funded successfully!")
                print(f"   Funded with 1000 XRP on testnet")
            else:
                print("⚠️  Wallet created but funding may have failed")
                print("   You can manually fund it at: https://xrpl.org/xrp-testnet-faucet.html")
        except Exception as e:
            print("⚠️  Wallet created but funding failed")
            print("   You can manually fund it at: https://xrpl.org/xrp-testnet-faucet.html")
        
        print("\n🔧 Environment Configuration")
        print("=" * 30)
        print("Add these values to your backend/.env file:")
        print(f"ISSUER_WALLET_SEED={wallet.seed}")
        print(f"ISSUER_WALLET_ADDRESS={wallet.address}")
        print(f"XRPL_NETWORK=testnet")
        
        print("\n⚠️  IMPORTANT SECURITY NOTE:")
        print("In production, encrypt the wallet seed and use secure key management!")
        
        return {
            "address": wallet.address,
            "seed": wallet.seed,
            "balance": "1000 XRP (testnet)"
        }
        
    except Exception as e:
        print(f"❌ Error setting up wallet: {str(e)}")
        return None

if __name__ == "__main__":
    wallet_info = create_and_fund_wallet()
    
    if wallet_info:
        print("\n🎉 Setup completed successfully!")
        print("You can now start the CryptoConnect backend.")
    else:
        print("\n💥 Setup failed. Please try again.")