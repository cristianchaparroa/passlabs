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
