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

    # Stablecoin Token Addresses - Scroll Sepolia Testnet
    USDC_ADDRESS: str = os.getenv(
        "USDC_ADDRESS", "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238"
    )
    USDT_ADDRESS: str = os.getenv(
        "USDT_ADDRESS", "0x186C0C26c45A8DA1Da34339ee513624a9609156d"
    )
    DAI_ADDRESS: str = os.getenv(
        "DAI_ADDRESS", "0x3e622317f8C93f7328350cF0B56d9eD4C620C5d6"
    )

    # DeFiLlama API</parameter>
    DEFI_LLAMA_API_URL: str = os.getenv(
        "DEFI_LLAMA_API_URL", "https://stablecoins.llama.fi/stablecoins"
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
