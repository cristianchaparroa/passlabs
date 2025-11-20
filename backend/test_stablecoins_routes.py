"""
Tests para los endpoints de stablecoins (FASE 5 - Testing & Polish)

Pruebas unitarias e integración para:
- GET /stablecoins/prices
- GET /stablecoins/prices/{symbol}
- GET /stablecoins/cache-info
- POST /stablecoins/cache-clear
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Agregar directorio padre al path
sys.path.insert(0, str(Path(__file__).parent))

from main import app


class TestStablecoinsRoutes:
    """Tests para los endpoints de stablecoins"""

    @pytest.fixture
    def client(self):
        """Fixture para cliente HTTP de prueba"""
        return TestClient(app)

    @pytest.fixture
    def mock_prices(self):
        """Fixture con datos de precios mockeados"""
        return [
            {
                "name": "USD Coin",
                "symbol": "USDC",
                "price_usd": 1.00,
                "market_cap": "33000000000",
                "change_24h": 0.01,
            },
            {
                "name": "Tether",
                "symbol": "USDT",
                "price_usd": 1.00,
                "market_cap": "96000000000",
                "change_24h": 0.02,
            },
            {
                "name": "Dai",
                "symbol": "DAI",
                "price_usd": 0.999,
                "market_cap": "5200000000",
                "change_24h": -0.01,
            },
        ]

    # ==================== TESTS GET /stablecoins/prices ====================

    def test_get_stablecoin_prices_success(self, client, mock_prices):
        """Test obtener todos los precios exitosamente"""
        with patch("routes.stablecoins.defi_llama_service") as mock_service:
            mock_service.get_stablecoin_prices = AsyncMock(return_value=mock_prices)

            response = client.get("/stablecoins/prices")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["count"] == 3
            assert len(data["data"]["stablecoins"]) == 3
            assert data["data"]["stablecoins"][0]["symbol"] == "USDC"

    def test_get_stablecoin_prices_empty(self, client):
        """Test obtener precios cuando no hay datos"""
        with patch("routes.stablecoins.defi_llama_service") as mock_service:
            mock_service.get_stablecoin_prices = AsyncMock(return_value=[])

            response = client.get("/stablecoins/prices")

            assert response.status_code == 200
            data = response.json()
            assert data["data"]["stablecoins"] == []
            assert "No price data available" in data["data"]["message"]

    def test_get_stablecoin_prices_service_error(self, client):
        """Test obtener precios con error en servicio"""
        with patch("routes.stablecoins.defi_llama_service") as mock_service:
            mock_service.get_stablecoin_prices = AsyncMock(
                side_effect=Exception("API error")
            )

            response = client.get("/stablecoins/prices")

            assert response.status_code == 500
            data = response.json()
            assert data["success"] is False

    def test_get_stablecoin_prices_service_not_available(self, client):
        """Test obtener precios cuando servicio no está disponible"""
        with patch("routes.stablecoins.defi_llama_service", None):
            response = client.get("/stablecoins/prices")

            assert response.status_code == 503
            data = response.json()
            assert "not available" in data["detail"].lower()

    def test_get_stablecoin_prices_has_last_updated(self, client, mock_prices):
        """Test que respuesta incluye last_updated"""
        with patch("routes.stablecoins.defi_llama_service") as mock_service:
            mock_prices_with_timestamp = mock_prices.copy()
            mock_prices_with_timestamp[0]["last_updated"] = "2024-01-01T12:00:00Z"
            mock_service.get_stablecoin_prices = AsyncMock(
                return_value=mock_prices_with_timestamp
            )

            response = client.get("/stablecoins/prices")

            assert response.status_code == 200
            data = response.json()
            assert "last_updated" in data

    # ==================== TESTS GET /stablecoins/prices/{symbol} ====================

    def test_get_specific_stablecoin_usdc(self, client):
        """Test obtener precio específico de USDC"""
        with patch("routes.stablecoins.defi_llama_service") as mock_service:
            mock_service.get_specific_stablecoin = AsyncMock(
                return_value={
                    "name": "USD Coin",
                    "symbol": "USDC",
                    "price_usd": 1.00,
                    "market_cap": "33000000000",
                    "change_24h": 0.01,
                }
            )

            response = client.get("/stablecoins/prices/USDC")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["symbol"] == "USDC"
            assert data["data"]["price_usd"] == 1.00

    def test_get_specific_stablecoin_lowercase(self, client):
        """Test obtener precio con símbolo en minúsculas"""
        with patch("routes.stablecoins.defi_llama_service") as mock_service:
            mock_service.get_specific_stablecoin = AsyncMock(
                return_value={
                    "name": "Tether",
                    "symbol": "USDT",
                    "price_usd": 1.00,
                }
            )

            response = client.get("/stablecoins/prices/usdt")

            assert response.status_code == 200
            data = response.json()
            assert data["data"]["symbol"] == "USDT"

    def test_get_specific_stablecoin_invalid_symbol(self, client):
        """Test obtener precio con símbolo inválido"""
        response = client.get("/stablecoins/prices/")

        # URL vacía, diferente error
        assert response.status_code == 404

    def test_get_specific_stablecoin_not_found(self, client):
        """Test obtener precio de stablecoin no existente"""
        with patch("routes.stablecoins.defi_llama_service") as mock_service:
            mock_service.get_specific_stablecoin = AsyncMock(return_value=None)

            response = client.get("/stablecoins/prices/FAKE")

            assert response.status_code == 404
            data = response.json()
            assert "not found" in data["detail"].lower()

    def test_get_specific_stablecoin_service_error(self, client):
        """Test obtener precio con error en servicio"""
        with patch("routes.stablecoins.defi_llama_service") as mock_service:
            mock_service.get_specific_stablecoin = AsyncMock(
                side_effect=Exception("API error")
            )

            response = client.get("/stablecoins/prices/USDC")

            assert response.status_code == 500

    # ==================== TESTS GET /stablecoins/cache-info ====================

    def test_get_cache_info_success(self, client):
        """Test obtener información del caché"""
        with patch("routes.stablecoins.defi_llama_service") as mock_service:
            mock_service.get_cache_info = MagicMock(
                return_value={
                    "cached": True,
                    "cache_timestamp": "2024-01-01T12:00:00Z",
                    "cache_ttl_seconds": 300,
                    "entries_count": 3,
                }
            )

            response = client.get("/stablecoins/cache-info")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["cached"] is True
            assert data["data"]["entries_count"] == 3

    def test_get_cache_info_empty_cache(self, client):
        """Test obtener info cuando caché está vacío"""
        with patch("routes.stablecoins.defi_llama_service") as mock_service:
            mock_service.get_cache_info = MagicMock(
                return_value={
                    "cached": False,
                    "cache_timestamp": None,
                    "entries_count": 0,
                }
            )

            response = client.get("/stablecoins/cache-info")

            assert response.status_code == 200
            data = response.json()
            assert data["data"]["cached"] is False

    def test_get_cache_info_service_error(self, client):
        """Test obtener info del caché con error"""
        with patch("routes.stablecoins.defi_llama_service") as mock_service:
            mock_service.get_cache_info = MagicMock(
                side_effect=Exception("Cache error")
            )

            response = client.get("/stablecoins/cache-info")

            assert response.status_code == 500

    # ==================== TESTS POST /stablecoins/cache-clear ====================

    def test_cache_clear_success(self, client):
        """Test limpiar caché exitosamente"""
        with patch("routes.stablecoins.defi_llama_service") as mock_service:
            mock_service.clear_cache = MagicMock()

            response = client.post("/stablecoins/cache-clear")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "cleared" in data["message"].lower()

    def test_cache_clear_verifies_call(self, client):
        """Test que clear_cache es realmente llamado"""
        with patch("routes.stablecoins.defi_llama_service") as mock_service:
            mock_service.clear_cache = MagicMock()

            client.post("/stablecoins/cache-clear")

            mock_service.clear_cache.assert_called_once()

    def test_cache_clear_service_error(self, client):
        """Test limpiar caché con error"""
        with patch("routes.stablecoins.defi_llama_service") as mock_service:
            mock_service.clear_cache = MagicMock(side_effect=Exception("Cache error"))

            response = client.post("/stablecoins/cache-clear")

            assert response.status_code == 500

    def test_cache_clear_service_not_available(self, client):
        """Test limpiar caché cuando servicio no está disponible"""
        with patch("routes.stablecoins.defi_llama_service", None):
            response = client.post("/stablecoins/cache-clear")

            assert response.status_code == 503


class TestStablecoinsValidation:
    """Tests para validaciones de stablecoins"""

    def test_symbol_lowercase_conversion(self, client):
        """Test que símbolo se convierte a mayúsculas"""
        with patch("routes.stablecoins.defi_llama_service") as mock_service:
            mock_service.get_specific_stablecoin = AsyncMock(
                return_value={"symbol": "USDC", "price_usd": 1.00}
            )

            response = client.get("/stablecoins/prices/usdc")

            assert response.status_code == 200
            # Verificar que se pasó en mayúsculas
            call_args = mock_service.get_specific_stablecoin.call_args
            assert call_args[0][0] == "USDC"

    def test_prices_have_required_fields(self, client):
        """Test que precios tienen campos requeridos"""
        mock_prices = [
            {
                "name": "USD Coin",
                "symbol": "USDC",
                "price_usd": 1.00,
                "market_cap": "33000000000",
                "change_24h": 0.01,
            }
        ]

        with patch("routes.stablecoins.defi_llama_service") as mock_service:
            mock_service.get_stablecoin_prices = AsyncMock(return_value=mock_prices)

            response = client.get("/stablecoins/prices")

            data = response.json()
            for coin in data["data"]["stablecoins"]:
                assert "symbol" in coin
                assert "price_usd" in coin
                assert "name" in coin


class TestStablecoinsIntegration:
    """Tests de integración para stablecoins"""

    def test_prices_and_cache_info_consistency(self, client):
        """Test consistencia entre precios e info de caché"""
        mock_prices = [
            {"symbol": "USDC", "price_usd": 1.00},
            {"symbol": "USDT", "price_usd": 1.00},
            {"symbol": "DAI", "price_usd": 0.999},
        ]

        with patch("routes.stablecoins.defi_llama_service") as mock_service:
            mock_service.get_stablecoin_prices = AsyncMock(return_value=mock_prices)
            mock_service.get_cache_info = MagicMock(
                return_value={
                    "cached": True,
                    "entries_count": 3,
                }
            )

            response_prices = client.get("/stablecoins/prices")
            response_cache = client.get("/stablecoins/cache-info")

            assert response_prices.json()["data"]["count"] == 3
            assert response_cache.json()["data"]["entries_count"] == 3

    def test_cache_clear_then_refresh(self, client):
        """Test limpiar caché y obtener precios frescos"""
        mock_prices = [{"symbol": "USDC", "price_usd": 1.00}]

        with patch("routes.stablecoins.defi_llama_service") as mock_service:
            mock_service.clear_cache = MagicMock()
            mock_service.get_stablecoin_prices = AsyncMock(return_value=mock_prices)

            # Limpiar caché
            response_clear = client.post("/stablecoins/cache-clear")
            assert response_clear.status_code == 200

            # Obtener precios frescos
            response_prices = client.get("/stablecoins/prices")
            assert response_prices.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
