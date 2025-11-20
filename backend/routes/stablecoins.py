from fastapi import APIRouter

router = APIRouter()


@router.get("/prices")
async def get_stablecoin_prices():
    """
    Obtener precios de stablecoins desde DeFiLlama API

    Returns:
        dict: Información de precios de USDC, USDT y DAI
    """
    pass
