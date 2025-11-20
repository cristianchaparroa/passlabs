import sys
from contextlib import asynccontextmanager
from datetime import datetime

# Enforce Python 3.13
if sys.version_info < (3, 13):
    raise RuntimeError("Python 3.13 or higher is required")

from config import settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from services.blockchain_service import blockchain_service
from services.defi_llama_service import defi_llama_service
from services.payment_service import PaymentService
from utils.logger import get_logger

# Configurar logging
logger = get_logger(__name__)

# Inicializar servicios globales
payment_service = None
services_ready = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager para el ciclo de vida de la aplicación
    Reemplaza on_event("startup") y on_event("shutdown")
    """
    global payment_service, services_ready

    # === STARTUP ===
    logger.info("=" * 60)
    logger.info("🚀 Starting Crypto Payments API v0.5.0")
    logger.info("=" * 60)

    try:
        # Verificar blockchain
        logger.info("📦 Initializing blockchain service...")
        if blockchain_service is None:
            logger.error("❌ Blockchain service initialization failed")
            raise RuntimeError("BlockchainService not available")

        if not blockchain_service.is_connected():
            logger.error("❌ Not connected to blockchain")
            raise RuntimeError("Cannot connect to blockchain RPC")

        logger.info("✅ Blockchain service ready")

        # Obtener información de la red
        try:
            network_info = blockchain_service.get_network_info()
            logger.info(f"   Chain ID: {network_info.get('chain_id')}")
            logger.info(f"   Latest Block: {network_info.get('latest_block')}")
            logger.info(f"   Gas Price: {network_info.get('gas_price')} Gwei")
            logger.info(f"   Account: {network_info.get('account')}")
        except Exception as e:
            logger.warning(f"⚠️  Could not get network info: {str(e)}")

        # Inicializar payment service
        logger.info("📦 Initializing payment service...")
        payment_service = PaymentService(blockchain_service)
        logger.info("✅ Payment service ready")

        # Pasar la instancia del servicio a las rutas
        from routes import payments as payments_router

        payments_router.set_payment_service(payment_service)
        logger.info("✅ Payment service instance set in routes")

        # Verificar DeFiLlama service
        logger.info("📦 Initializing DeFiLlama service...")
        if defi_llama_service is None:
            logger.error("❌ DeFiLlama service initialization failed")
            raise RuntimeError("DeFiLlamaService not available")

        logger.info("✅ DeFiLlama service ready")

        # Intentar obtener precios iniciales
        logger.info("📡 Fetching initial stablecoin prices...")
        try:
            prices = await defi_llama_service.get_stablecoin_prices()
            logger.info(f"✅ Retrieved {len(prices)} stablecoin prices")
            for price in prices:
                logger.info(f"   {price['symbol']}: ${price['price_usd']}")
        except Exception as e:
            logger.warning(f"⚠️  Could not fetch initial prices: {str(e)}")

        services_ready = True
        logger.info("=" * 60)
        logger.info("✅ All services initialized successfully!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}")
        services_ready = False
        raise

    # === SERVE ===
    yield

    # === SHUTDOWN ===
    logger.info("🛑 Shutting down Crypto Payments API")
    logger.info("Goodbye!")


# Crear aplicación FastAPI con lifespan
app = FastAPI(
    title="Crypto Payments API",
    description="MVP de sistema de pagos con criptomonedas en Scroll Sepolia",
    version="0.5.0",
    lifespan=lifespan,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== ENDPOINTS ====================


@app.get("/health")
async def health_check():
    """
    Endpoint para verificar que la API está en línea

    Returns:
        dict: Estado de salud de la API
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "Crypto Payments API",
        "version": "0.5.0",
        "services_ready": services_ready,
    }


@app.get("/")
async def root():
    """
    Endpoint raíz con información de la API

    Returns:
        dict: Información general de la API
    """
    return {
        "message": "Welcome to Crypto Payments API (MVP - Hackathon)",
        "version": "0.5.0",
        "phase": "Phase 5 - Testing & Polish",
        "status": "running" if services_ready else "initializing",
        "endpoints": {
            "health": "/health",
            "payments_create": "/payments/create",
            "payments_status": "/payments/status/{tx_hash}",
            "payments_by_id": "/payments/by-id/{payment_id}",
            "payments_all": "/payments/all",
            "payments_by_status": "/payments/by-status/{status}",
            "stablecoins_prices": "/stablecoins/prices",
            "stablecoins_price_specific": "/stablecoins/prices/{symbol}",
            "stablecoins_cache_info": "/stablecoins/cache-info",
            "stablecoins_cache_clear": "/stablecoins/cache-clear",
            "docs": "/docs",
            "redoc": "/redoc",
        },
        "blockchain": {
            "network": "Scroll Sepolia Testnet",
            "chain_id": settings.CHAIN_ID,
        },
    }


@app.get("/status")
async def api_status():
    """
    Endpoint de estado detallado de la API

    Returns:
        dict: Estado detallado con información de servicios
    """
    try:
        blockchain_info = (
            blockchain_service.get_network_info()
            if blockchain_service
            else {"error": "Service not available"}
        )
    except Exception as e:
        blockchain_info = {"error": str(e)}

    try:
        defi_cache_info = (
            defi_llama_service.get_cache_info()
            if defi_llama_service
            else {"error": "Service not available"}
        )
    except Exception as e:
        defi_cache_info = {"error": str(e)}

    try:
        payment_stats = (
            payment_service.get_payment_statistics()
            if payment_service
            else {"error": "Service not available"}
        )
    except Exception as e:
        payment_stats = {"error": str(e)}

    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "0.5.0",
        "phase": "Phase 5 - Testing & Polish",
        "services": {
            "blockchain": {
                "status": "ready" if blockchain_service else "error",
                "info": blockchain_info,
            },
            "payment": {
                "status": "ready" if payment_service else "error",
                "stats": payment_stats,
            },
            "defi_llama": {
                "status": "ready" if defi_llama_service else "error",
                "cache": defi_cache_info,
            },
        },
    }


# ==================== ERROR HANDLERS ====================


@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Manejador para ValueError"""
    logger.error(f"ValueError: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": "Validation Error",
            "message": str(exc),
        },
    )


@app.exception_handler(RuntimeError)
async def runtime_error_handler(request, exc):
    """Manejador para RuntimeError"""
    logger.error(f"RuntimeError: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Runtime Error",
            "message": str(exc),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Manejador global de excepciones"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal Server Error",
            "message": str(exc) if settings.DEBUG else "An error occurred",
        },
    )


# ==================== ROUTERS ====================

# Importar rutas al final para evitar circular imports
from routes import payments, stablecoins

# Incluir rutas
app.include_router(payments.router, prefix="/payments", tags=["Payments"])
app.include_router(stablecoins.router, prefix="/stablecoins", tags=["Stablecoins"])


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting server on {settings.API_HOST}:{settings.API_PORT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"API Docs: http://{settings.API_HOST}:{settings.API_PORT}/docs")

    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
