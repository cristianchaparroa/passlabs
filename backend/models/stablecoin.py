from typing import Optional

from pydantic import BaseModel


class StablecoinPrice(BaseModel):
    """Modelo para un precio de stablecoin"""

    name: str
    symbol: str
    price_usd: float
    market_cap: str
    change_24h: float


class StablecoinPricesResponse(BaseModel):
    """Modelo de respuesta con precios de stablecoins"""

    success: bool
    data: dict
    last_updated: str
