"""
Configuración de pytest para todos los tests

Este archivo es automáticamente detectado por pytest y proporciona:
- Fixtures compartidas entre tests
- Configuración de sesión
- Hooks de pytest
"""

import sys
from pathlib import Path

# Agregar el directorio backend al path para que los imports funcionen correctamente
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def test_app():
    """Fixture de sesión para la aplicación FastAPI"""
    from main import app

    return app


@pytest.fixture
def client(test_app):
    """Fixture para el cliente de prueba de FastAPI"""
    return TestClient(test_app)


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Fixture para mockear variables de entorno"""
    test_env = {
        "PRIVATE_KEY": "0x" + "1" * 64,
        "CONTRACT_ADDRESS": "0x" + "0" * 40,
        "RPC_URL": "https://scroll-sepolia-rpc.example.com",
        "NETWORK_ID": "534351",
        "LOG_LEVEL": "DEBUG",
    }
    for key, value in test_env.items():
        monkeypatch.setenv(key, value)
    return test_env


@pytest.fixture
def mock_blockchain_service(mocker):
    """Fixture para mockear el servicio de blockchain"""
    from services.blockchain_service import BlockchainService

    mock_service = mocker.MagicMock(spec=BlockchainService)
    mock_service.is_connected.return_value = True
    mock_service.get_web3_instance.return_value = mocker.MagicMock()

    return mock_service


@pytest.fixture
def mock_payment_service(mocker):
    """Fixture para mockear el servicio de pagos"""
    from services.payment_service import PaymentService

    mock_service = mocker.MagicMock(spec=PaymentService)
    mock_service.create_payment.return_value = {
        "payment_id": "test_payment_123",
        "tx_hash": "0x" + "0" * 64,
        "status": "pending",
    }

    return mock_service


@pytest.fixture
def mock_defi_llama_service(mocker):
    """Fixture para mockear el servicio de DeFi Llama"""
    from services.defi_llama_service import DeFiLlamaService

    mock_service = mocker.MagicMock(spec=DeFiLlamaService)
    mock_service.get_stablecoin_prices.return_value = {
        "USDC": 1.0,
        "USDT": 1.0,
        "DAI": 1.0,
    }

    return mock_service


@pytest.fixture
def sample_payment_data():
    """Fixture con datos de prueba para pagos"""
    return {
        "user_wallet": "0x" + "a" * 40,
        "amount": 100.0,
        "stablecoin": "USDC",
        "description": "Test payment",
    }


@pytest.fixture
def sample_payment_response():
    """Fixture con respuesta de pago de prueba"""
    return {
        "success": True,
        "payment_id": "test_payment_123",
        "tx_hash": "0x" + "b" * 64,
        "status": "pending",
        "amount": 100.0,
        "stablecoin": "USDC",
        "created_at": "2024-01-01T00:00:00Z",
    }


def pytest_configure(config):
    """Hook para configurar pytest antes de ejecutar tests"""
    config.addinivalue_line("markers", "unit: marca test como prueba unitaria")
    config.addinivalue_line(
        "markers", "integration: marca test como prueba de integración"
    )
    config.addinivalue_line("markers", "slow: marca test como lento")


def pytest_collection_modifyitems(config, items):
    """Hook para modificar los items recolectados por pytest"""
    for item in items:
        # Si no tiene marcador, marcar como unit
        if not any(
            marker.name in ["unit", "integration", "slow"]
            for marker in item.iter_markers()
        ):
            item.add_marker(pytest.mark.unit)
