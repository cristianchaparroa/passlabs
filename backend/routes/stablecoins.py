import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from services.defi_llama_service import defi_llama_service
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/prices")
async def get_stablecoin_prices():
    """
    Obtener precios actualizados de stablecoins desde DeFiLlama API

    Endpoint: GET /stablecoins/prices

    Returns:
        dict: Lista de stablecoins con sus precios, capitalización de mercado y cambio 24h

    Raises:
        HTTPException 500: Error al obtener precios
    """
    try:
        logger.info("📡 Fetching stablecoin prices from DeFiLlama")

        if defi_llama_service is None:
            logger.error("DeFiLlama service not initialized")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Stablecoin price service not available",
            )

        # Obtener precios desde el servicio
        prices = await defi_llama_service.get_stablecoin_prices()

        if not prices:
            logger.warning("⚠️  No prices retrieved from API")
            return {
                "success": True,
                "data": {
                    "stablecoins": [],
                    "message": "No price data available",
                },
                "last_updated": None,
            }

        logger.info(f"✅ Retrieved {len(prices)} stablecoin prices")

        return {
            "success": True,
            "data": {
                "stablecoins": prices,
                "count": len(prices),
            },
            "last_updated": prices[0].get("last_updated") if prices else None,
        }

    except Exception as e:
        logger.error(f"❌ Error fetching stablecoin prices: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching stablecoin prices",
        )


@router.get("/prices/{symbol}")
async def get_stablecoin_price(symbol: str):
    """
    Obtener precio de un stablecoin específico

    Endpoint: GET /stablecoins/prices/{symbol}

    Args:
        symbol: Símbolo del stablecoin (USDC, USDT, DAI, etc.)

    Returns:
        dict: Información del precio del stablecoin

    Raises:
        HTTPException 400: Símbolo inválido
        HTTPException 404: Stablecoin no encontrado
        HTTPException 500: Error al obtener precio
    """
    try:
        if not symbol or not isinstance(symbol, str) or len(symbol) == 0:
            logger.warning(f"⚠️  Invalid symbol: {symbol}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid stablecoin symbol",
            )

        symbol_upper = symbol.upper()
        logger.info(f"🔍 Fetching price for stablecoin: {symbol_upper}")

        if defi_llama_service is None:
            logger.error("DeFiLlama service not initialized")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Stablecoin price service not available",
            )

        # Obtener precio específico
        price_data = await defi_llama_service.get_specific_stablecoin(symbol_upper)

        if not price_data:
            logger.warning(f"⚠️  Stablecoin not found: {symbol_upper}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Stablecoin '{symbol_upper}' not found",
            )

        logger.info(
            f"✅ Retrieved price for {symbol_upper}: ${price_data.get('price_usd')}"
        )

        return {
            "success": True,
            "data": price_data,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching price for {symbol}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching stablecoin price",
        )


@router.get("/cache-info")
async def get_cache_info():
    """
    Obtener información del caché de precios

    Endpoint: GET /stablecoins/cache-info

    Returns:
        dict: Información sobre el estado del caché

    Raises:
        HTTPException 500: Error al obtener información del caché
    """
    try:
        logger.info("📊 Getting cache information")

        if defi_llama_service is None:
            logger.error("DeFiLlama service not initialized")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Stablecoin price service not available",
            )

        # Obtener información del caché
        cache_info = defi_llama_service.get_cache_info()

        logger.info("✅ Cache info retrieved")

        return {
            "success": True,
            "data": cache_info,
        }

    except Exception as e:
        logger.error(f"❌ Error getting cache info: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving cache information",
        )


@router.post("/cache-clear")
async def clear_price_cache():
    """
    Limpiar el caché de precios para forzar actualización en la próxima solicitud

    Endpoint: POST /stablecoins/cache-clear

    Returns:
        dict: Confirmación de limpieza del caché

    Raises:
        HTTPException 500: Error al limpiar caché
    """
    try:
        logger.info("🗑️  Clearing price cache")

        if defi_llama_service is None:
            logger.error("DeFiLlama service not initialized")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Stablecoin price service not available",
            )

        # Limpiar caché
        defi_llama_service.clear_cache()

        logger.info("✅ Price cache cleared successfully")

        return {
            "success": True,
            "message": "Cache cleared successfully. Next request will fetch fresh prices.",
        }

    except Exception as e:
        logger.error(f"❌ Error clearing cache: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error clearing cache",
        )
