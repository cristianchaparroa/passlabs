"""
Script de prueba para verificar que el setup de la aplicación es correcto
"""

import sys
from pathlib import Path

# Agregar directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_imports():
    """Verificar que todos los imports funcionan correctamente"""
    print("🔍 Verificando imports...")
    try:
        from config import settings

        print("✅ config importado correctamente")

        from utils.logger import get_logger

        print("✅ logger importado correctamente")

        from utils.validators import is_valid_ethereum_address

        print("✅ validators importado correctamente")

        from utils.constants import SUPPORTED_STABLECOINS

        print("✅ constants importado correctamente")

        from models.payment import CreatePaymentRequest, PaymentResponse

        print("✅ models.payment importado correctamente")

        from models.stablecoin import StablecoinPrice, StablecoinPricesResponse

        print("✅ models.stablecoin importado correctamente")

        from services.blockchain_service import blockchain_service

        print("✅ blockchain_service importado correctamente")

        from services.payment_service import PaymentService

        print("✅ payment_service importado correctamente")

        from services.defi_llama_service import defi_llama_service

        print("✅ defi_llama_service importado correctamente")

        return True
    except ImportError as e:
        print(f"❌ Error de import: {e}")
        return False


def test_config():
    """Verificar que la configuración está correcta"""
    print("\n🔍 Verificando configuración...")
    try:
        from config import settings

        print(f"  Network: {settings.NETWORK}")
        print(f"  RPC URL: {settings.RPC_URL}")
        print(f"  Chain ID: {settings.CHAIN_ID}")
        print(f"  API Host: {settings.API_HOST}")
        print(f"  API Port: {settings.API_PORT}")
        print(f"  Debug: {settings.DEBUG}")
        print(f"  Cache TTL: {settings.CACHE_TTL}s")
        print(f"  Stablecoins: {settings.STABLECOINS}")

        if not settings.PRIVATE_KEY:
            print("⚠️  PRIVATE_KEY no está configurada en .env")
        else:
            print("✅ PRIVATE_KEY está configurada")

        if (
            not settings.CONTRACT_ADDRESS
            or settings.CONTRACT_ADDRESS == "0x0000000000000000000000000000000000000000"
        ):
            print("⚠️  CONTRACT_ADDRESS no está configurada o es placeholder")
        else:
            print("✅ CONTRACT_ADDRESS está configurada")

        print("✅ Configuración cargada correctamente")
        return True
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        return False


def test_validators():
    """Verificar que los validadores funcionan"""
    print("\n🔍 Verificando validadores...")
    try:
        from utils.validators import (
            is_valid_amount,
            is_valid_ethereum_address,
            is_valid_stablecoin,
            is_valid_tx_hash,
        )

        # Probar validador de dirección
        valid_address = "0x742d35Cc6634C0532925a3b844Bc9e7595f1bEb"
        invalid_address = "0xinvalid"

        assert is_valid_ethereum_address(valid_address), "Dirección válida rechazada"
        assert not is_valid_ethereum_address(invalid_address), (
            "Dirección inválida aceptada"
        )
        print("✅ Validador de direcciones funciona")

        # Probar validador de cantidad
        assert is_valid_amount(100.5), "Cantidad válida rechazada"
        assert not is_valid_amount(0.001), "Cantidad muy pequeña aceptada"
        assert not is_valid_amount(2_000_000), "Cantidad muy grande aceptada"
        print("✅ Validador de cantidad funciona")

        # Probar validador de stablecoin
        assert is_valid_stablecoin("USDC"), "USDC rechazado"
        assert is_valid_stablecoin("usdc"), "USDC en minúsculas rechazado"
        assert not is_valid_stablecoin("INVALID"), "Stablecoin inválido aceptado"
        print("✅ Validador de stablecoin funciona")

        return True
    except AssertionError as e:
        print(f"❌ Error en validador: {e}")
        return False
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False


def test_blockchain_connection():
    """Verificar conexión a blockchain"""
    print("\n🔍 Verificando conexión a blockchain...")
    try:
        from services.blockchain_service import blockchain_service

        is_connected = blockchain_service.is_connected()
        if is_connected:
            print("✅ Conectado a blockchain (Scroll Sepolia)")
        else:
            print("❌ No se pudo conectar a blockchain")

        return is_connected
    except Exception as e:
        print(f"❌ Error conectando a blockchain: {e}")
        return False


def main():
    """Ejecutar todas las pruebas"""
    print("=" * 60)
    print("🧪 PRUEBA DE SETUP - Crypto Payments API")
    print("=" * 60)

    results = {
        "imports": test_imports(),
        "config": test_config(),
        "validators": test_validators(),
        "blockchain": test_blockchain_connection(),
    }

    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)

    for test_name, result in results.items():
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name.upper()}: {status}")

    all_passed = all(results.values())

    print("=" * 60)
    if all_passed:
        print("✅ TODAS LAS PRUEBAS PASARON - Setup correcto!")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON - Revisa los errores arriba")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
