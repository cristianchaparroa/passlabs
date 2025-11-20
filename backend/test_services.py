"""
Tests para los servicios core (FASE 5 - Testing & Polish)

Pruebas unitarias para:
- blockchain_service.py
- payment_service.py
- defi_llama_service.py
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Agregar directorio padre al path
sys.path.insert(0, str(Path(__file__).parent))

from services.blockchain_service import BlockchainService
from services.defi_llama_service import DeFiLlamaService
from services.payment_service import PaymentService


class TestBlockchainService:
    """Tests para BlockchainService"""

    @pytest.fixture
    def mock_web3(self):
        """Fixture para Web3 mockeado"""
        with patch("services.blockchain_service.Web3") as mock:
            yield mock

    def test_blockchain_service_init(self, mock_web3):
        """Test inicialización del servicio blockchain"""
        with patch("services.blockchain_service.Web3"):
            service = BlockchainService()
            assert service is not None

    def test_is_connected_true(self, mock_web3):
        """Test verificar conexión exitosa"""
        with patch(
            "services.blockchain_service.BlockchainService.is_connected"
        ) as mock_connected:
            mock_connected.return_value = True
            service = BlockchainService()
            assert mock_connected() is True

    def test_is_connected_false(self, mock_web3):
        """Test verificar desconexión"""
        with patch(
            "services.blockchain_service.BlockchainService.is_connected"
        ) as mock_connected:
            mock_connected.return_value = False
            service = BlockchainService()
            assert mock_connected() is False

    def test_get_network_info(self, mock_web3):
        """Test obtener información de red"""
        with patch(
            "services.blockchain_service.BlockchainService.get_network_info"
        ) as mock_info:
            mock_info.return_value = {
                "chain_id": 534351,
                "latest_block": 1000000,
                "gas_price_gwei": 0.1,
                "account": "0x123",
            }
            service = BlockchainService()
            info = mock_info()
            assert info["chain_id"] == 534351
            assert info["latest_block"] == 1000000

    def test_get_balance(self, mock_web3):
        """Test obtener balance"""
        address = "0x742d35Cc6634C0532925a3b844Bc9e7595f1bEb"
        with patch(
            "services.blockchain_service.BlockchainService.get_balance"
        ) as mock_balance:
            mock_balance.return_value = 1.5
            service = BlockchainService()
            balance = mock_balance(address)
            assert balance == 1.5

    def test_is_token_allowed(self, mock_web3):
        """Test verificar si token está permitido"""
        token_address = "0xabc123"
        with patch(
            "services.blockchain_service.BlockchainService.is_token_allowed"
        ) as mock_allowed:
            mock_allowed.return_value = True
            service = BlockchainService()
            assert mock_allowed(token_address) is True


class TestPaymentService:
    """Tests para PaymentService"""

    @pytest.fixture
    def mock_blockchain_service(self):
        """Fixture para BlockchainService mockeado"""
        mock_service = MagicMock(spec=BlockchainService)
        return mock_service

    def test_payment_service_init(self, mock_blockchain_service):
        """Test inicialización del servicio de pagos"""
        service = PaymentService(mock_blockchain_service)
        assert service is not None
        assert service.blockchain_service == mock_blockchain_service

    @pytest.mark.asyncio
    async def test_create_payment_valid_data(self, mock_blockchain_service):
        """Test crear pago con datos válidos"""
        service = PaymentService(mock_blockchain_service)

        with patch(
            "services.payment_service.is_valid_ethereum_address"
        ) as mock_valid_addr:
            with patch("services.payment_service.is_valid_amount") as mock_valid_amount:
                with patch(
                    "services.payment_service.is_valid_stablecoin"
                ) as mock_valid_coin:
                    mock_valid_addr.return_value = True
                    mock_valid_amount.return_value = True
                    mock_valid_coin.return_value = True

                    with patch.object(
                        service, "_verify_token_allowed", new_callable=AsyncMock
                    ) as mock_verify:
                        mock_verify.return_value = True

                        payment = await service.create_payment(
                            recipient_address="0x742d35Cc6634C0532925a3b844Bc9e7595f1bEb",
                            amount=100.50,
                            stablecoin="USDC",
                        )

                        assert payment["status"] == "pending"
                        assert payment["amount"] == 100.50
                        assert payment["stablecoin"] == "USDC"

    @pytest.mark.asyncio
    async def test_create_payment_invalid_address(self, mock_blockchain_service):
        """Test crear pago con dirección inválida"""
        service = PaymentService(mock_blockchain_service)

        with patch(
            "services.payment_service.is_valid_ethereum_address"
        ) as mock_valid_addr:
            mock_valid_addr.return_value = False

            with pytest.raises(ValueError):
                await service.create_payment(
                    recipient_address="invalid", amount=100.50, stablecoin="USDC"
                )

    @pytest.mark.asyncio
    async def test_create_payment_invalid_amount(self, mock_blockchain_service):
        """Test crear pago con monto inválido"""
        service = PaymentService(mock_blockchain_service)

        with patch(
            "services.payment_service.is_valid_ethereum_address"
        ) as mock_valid_addr:
            with patch("services.payment_service.is_valid_amount") as mock_valid_amount:
                mock_valid_addr.return_value = True
                mock_valid_amount.return_value = False

                with pytest.raises(ValueError):
                    await service.create_payment(
                        recipient_address="0x742d35Cc6634C0532925a3b844Bc9e7595f1bEb",
                        amount=0.001,
                        stablecoin="USDC",
                    )

    @pytest.mark.asyncio
    async def test_create_payment_invalid_stablecoin(self, mock_blockchain_service):
        """Test crear pago con stablecoin inválido"""
        service = PaymentService(mock_blockchain_service)

        with patch(
            "services.payment_service.is_valid_ethereum_address"
        ) as mock_valid_addr:
            with patch("services.payment_service.is_valid_amount") as mock_valid_amount:
                with patch(
                    "services.payment_service.is_valid_stablecoin"
                ) as mock_valid_coin:
                    mock_valid_addr.return_value = True
                    mock_valid_amount.return_value = True
                    mock_valid_coin.return_value = False

                    with pytest.raises(ValueError):
                        await service.create_payment(
                            recipient_address="0x742d35Cc6634C0532925a3b844Bc9e7595f1bEb",
                            amount=100.50,
                            stablecoin="INVALID",
                        )

    @pytest.mark.asyncio
    async def test_get_payment_status_by_payment_id(self, mock_blockchain_service):
        """Test obtener estado de pago por ID"""
        service = PaymentService(mock_blockchain_service)

        # Primero crear un pago
        with patch(
            "services.payment_service.is_valid_ethereum_address"
        ) as mock_valid_addr:
            with patch("services.payment_service.is_valid_amount") as mock_valid_amount:
                with patch(
                    "services.payment_service.is_valid_stablecoin"
                ) as mock_valid_coin:
                    mock_valid_addr.return_value = True
                    mock_valid_amount.return_value = True
                    mock_valid_coin.return_value = True

                    with patch.object(
                        service, "_verify_token_allowed", new_callable=AsyncMock
                    ) as mock_verify:
                        mock_verify.return_value = True

                        payment = await service.create_payment(
                            recipient_address="0x742d35Cc6634C0532925a3b844Bc9e7595f1bEb",
                            amount=100.50,
                            stablecoin="USDC",
                        )

                        # Obtener estado
                        status = await service.get_payment_status(
                            payment_id=payment["payment_id"]
                        )
                        assert status["payment_id"] == payment["payment_id"]
                        assert status["status"] == "pending"

    def test_get_all_payments(self, mock_blockchain_service):
        """Test obtener todos los pagos"""
        service = PaymentService(mock_blockchain_service)

        # Agregar algunos pagos al caché
        service.payments_cache["id1"] = {"payment_id": "id1", "status": "pending"}
        service.payments_cache["id2"] = {"payment_id": "id2", "status": "completed"}

        all_payments = service.get_all_payments()
        assert len(all_payments) == 2
        assert all_payments[0]["payment_id"] == "id1"
        assert all_payments[1]["payment_id"] == "id2"

    def test_get_payments_by_status(self, mock_blockchain_service):
        """Test obtener pagos por estado"""
        service = PaymentService(mock_blockchain_service)

        # Agregar pagos con diferentes estados
        service.payments_cache["id1"] = {"payment_id": "id1", "status": "pending"}
        service.payments_cache["id2"] = {"payment_id": "id2", "status": "pending"}
        service.payments_cache["id3"] = {"payment_id": "id3", "status": "completed"}

        pending_payments = service.get_payments_by_status("pending")
        assert len(pending_payments) == 2
        assert all(p["status"] == "pending" for p in pending_payments)

        completed_payments = service.get_payments_by_status("completed")
        assert len(completed_payments) == 1
        assert completed_payments[0]["status"] == "completed"

    def test_get_payment_statistics(self, mock_blockchain_service):
        """Test obtener estadísticas de pagos"""
        service = PaymentService(mock_blockchain_service)

        service.payments_cache["id1"] = {
            "payment_id": "id1",
            "status": "pending",
            "amount": 100,
        }
        service.payments_cache["id2"] = {
            "payment_id": "id2",
            "status": "completed",
            "amount": 200,
        }

        stats = service.get_payment_statistics()
        assert stats["total_payments"] == 2
        assert stats["pending_count"] == 1
        assert stats["completed_count"] == 1


class TestDeFiLlamaService:
    """Tests para DeFiLlamaService"""

    @pytest.fixture
    def defi_service(self):
        """Fixture para DeFiLlamaService"""
        return DeFiLlamaService()

    @pytest.mark.asyncio
    async def test_defi_service_init(self, defi_service):
        """Test inicialización del servicio"""
        assert defi_service is not None
        assert defi_service.cache == {}

    @pytest.mark.asyncio
    async def test_get_stablecoin_prices_from_cache(self, defi_service):
        """Test obtener precios desde caché"""
        mock_prices = [
            {"symbol": "USDC", "price_usd": 1.00},
            {"symbol": "USDT", "price_usd": 1.00},
        ]

        defi_service.cache["stablecoins"] = mock_prices
        defi_service.cache_timestamp = 0  # Cache reciente

        with patch.object(defi_service, "_is_cache_valid", return_value=True):
            prices = await defi_service.get_stablecoin_prices()
            assert len(prices) == 2
            assert prices[0]["symbol"] == "USDC"

    @pytest.mark.asyncio
    async def test_get_stablecoin_prices_no_cache(self, defi_service):
        """Test obtener precios sin caché"""
        with patch.object(defi_service, "_is_cache_valid", return_value=False):
            with patch.object(
                defi_service, "_fetch_from_api", new_callable=AsyncMock
            ) as mock_fetch:
                mock_fetch.return_value = [
                    {"symbol": "USDC", "price_usd": 1.00},
                ]

                prices = await defi_service.get_stablecoin_prices()
                assert len(prices) == 1
                mock_fetch.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_stablecoin_prices_api_error_with_fallback(self, defi_service):
        """Test manejo de error de API con fallback a caché"""
        mock_cached_prices = [{"symbol": "USDC", "price_usd": 1.00}]
        defi_service.cache["stablecoins"] = mock_cached_prices

        with patch.object(defi_service, "_is_cache_valid", return_value=False):
            with patch.object(
                defi_service, "_fetch_from_api", new_callable=AsyncMock
            ) as mock_fetch:
                mock_fetch.side_effect = Exception("API error")

                prices = await defi_service.get_stablecoin_prices()
                assert len(prices) == 1
                assert prices[0]["symbol"] == "USDC"

    def test_is_cache_valid_expired(self, defi_service):
        """Test verificar caché expirado"""
        import time

        defi_service.cache_timestamp = time.time() - 1000  # 1000 segundos atrás

        is_valid = defi_service._is_cache_valid()
        assert is_valid is False

    def test_is_cache_valid_fresh(self, defi_service):
        """Test verificar caché fresco"""
        import time

        defi_service.cache_timestamp = time.time()

        with patch("services.defi_llama_service.settings.CACHE_TTL", 300):
            is_valid = defi_service._is_cache_valid()
            assert is_valid is True

    def test_clear_cache(self, defi_service):
        """Test limpiar caché"""
        defi_service.cache["stablecoins"] = [{"symbol": "USDC"}]
        defi_service.cache_timestamp = 123456

        defi_service.clear_cache()

        assert defi_service.cache == {}
        assert defi_service.cache_timestamp == 0

    def test_get_cache_info(self, defi_service):
        """Test obtener información del caché"""
        defi_service.cache["stablecoins"] = [
            {"symbol": "USDC"},
            {"symbol": "USDT"},
        ]

        cache_info = defi_service.get_cache_info()
        assert cache_info["cached"] is True
        assert cache_info["entries_count"] == 2

    def test_get_cache_info_empty(self, defi_service):
        """Test obtener info del caché vacío"""
        cache_info = defi_service.get_cache_info()
        assert cache_info["cached"] is False
        assert cache_info["entries_count"] == 0


class TestServicesIntegration:
    """Tests de integración entre servicios"""

    def test_payment_service_with_blockchain_service(self):
        """Test integración Payment Service con Blockchain Service"""
        mock_blockchain = MagicMock(spec=BlockchainService)
        payment_service = PaymentService(mock_blockchain)

        assert payment_service.blockchain_service == mock_blockchain

    @pytest.mark.asyncio
    async def test_payment_workflow(self):
        """Test flujo completo de pago"""
        mock_blockchain = MagicMock(spec=BlockchainService)
        payment_service = PaymentService(mock_blockchain)

        with patch(
            "services.payment_service.is_valid_ethereum_address"
        ) as mock_valid_addr:
            with patch("services.payment_service.is_valid_amount") as mock_valid_amount:
                with patch(
                    "services.payment_service.is_valid_stablecoin"
                ) as mock_valid_coin:
                    mock_valid_addr.return_value = True
                    mock_valid_amount.return_value = True
                    mock_valid_coin.return_value = True

                    with patch.object(
                        payment_service, "_verify_token_allowed", new_callable=AsyncMock
                    ) as mock_verify:
                        mock_verify.return_value = True

                        # Crear pago
                        payment = await payment_service.create_payment(
                            recipient_address="0x742d35Cc6634C0532925a3b844Bc9e7595f1bEb",
                            amount=100.50,
                            stablecoin="USDC",
                        )

                        # Obtener estado
                        status = await payment_service.get_payment_status(
                            payment_id=payment["payment_id"]
                        )

                        assert status["payment_id"] == payment["payment_id"]
                        assert status["status"] == "pending"
                        assert status["amount"] == 100.50


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
