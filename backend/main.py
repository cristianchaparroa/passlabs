import logging
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Importar rutas
from routes import payments, stablecoins

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="Crypto Payments API",
    description="MVP de sistema de pagos con criptomonedas en Scroll Sepolia",
    version="0.1.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Incluir rutas
app.include_router(payments.router, prefix="/payments", tags=["Payments"])
app.include_router(stablecoins.router, prefix="/stablecoins", tags=["Stablecoins"])


# Health Check
@app.get("/health")
async def health_check():
    """Endpoint para verificar que la API está en línea"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "Crypto Payments API",
    }


# Root endpoint
@app.get("/")
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "Welcome to Crypto Payments API (MVP - Hackathon)",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "payments": "/payments",
            "stablecoins": "/stablecoins",
        },
    }


# Error handler global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Manejador global de excepciones"""
    logger.error(f"Error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "message": str(exc) if app.debug else "An error occurred",
        },
    )


if __name__ == "__main__":
    import uvicorn
    from config import settings

    uvicorn.run(
        app, host=settings.API_HOST, port=settings.API_PORT, reload=settings.DEBUG
    )
