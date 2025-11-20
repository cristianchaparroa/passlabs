import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configuración global de la aplicación"""

    # Blockchain Configuration
    NETWORK: str = os.getenv("NETWORK", "scroll-sepolia")
    RPC_URL: str = os.getenv("RPC_URL", "https://sepolia-rpc.scroll.io/")
    PRIVATE_KEY: str = os.getenv("PRIVATE_KEY", "")
    CONTRACT_ADDRESS: str = os.getenv("CONTRACT_ADDRESS", "")
    CHAIN_ID: int = int(os.getenv("CHAIN_ID", "534351"))
    ETHERSCAN_API_KEY: str = os.getenv("ETHERSCAN_API_KEY", "")
    
    # Stablecoin Token Addresses (Scroll Sepolia Testnet)
    USDC_ADDRESS: str = os.getenv("USDC_ADDRESS", "0x06eFdBFf2a14a7c8E15944D1F4A48F9F95F663A4")
    USDT_ADDRESS: str = os.getenv("USDT_ADDRESS", "0xf55BEC9cafDbE8730f096Aa55dad6D22d44099Df")
    DAI_ADDRESS: str = os.getenv("DAI_ADDRESS", "0xcA77eB3fEFe3725Dc33bccB54eDEFc3D9f764f97")

    # DeFiLlama API
    DEFI_LLAMA_API_URL: str = os.getenv(
        "DEFI_LLAMA_API_URL",
        "https://stablecoins.llama.fi/stablecoins"
    )
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "300"))  # 5 minutos

    # FastAPI
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Stablecoins
    STABLECOINS: list = ["USDC", "USDT", "DAI"]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
