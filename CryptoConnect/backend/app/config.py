from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    mongodb_url: str = "mongodb://localhost:27017/cryptoconnect"
    
    # JWT
    jwt_secret_key: str = "your-super-secret-jwt-key-here-change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    
    # XRPL
    xrpl_network: str = "testnet"
    issuer_wallet_seed: Optional[str] = None
    issuer_wallet_address: Optional[str] = None
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    class Config:
        env_file = ".env"


settings = Settings()