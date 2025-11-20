"""
Tests para los endpoints de pagos (FASE 5 - Testing & Polish)

Pruebas unitarias e integración para:
- POST /payments/create
- GET /payments/status/{tx_hash}
- GET /payments/by-id/{payment_id}
- GET /payments/all
- GET /payments/by-status/{status}
"""

import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Agregar directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app
from models.payment import CreatePaymentRequest


class TestPaymentRoutes:
    """Tests para los endpoints de pagos"""

    @pytest.fixture
    def client(self):
        """Fixture para cliente HTTP de prueba"""
        return TestClient(app)

    @pytest.fixture
    def valid_payment_request(self):
        """Fixture con datos válidos para crear pago"""
        return {
            "recipient_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f1bEb",
            "amount": 100.50,
            "stablecoin": "USDC",
            "description": "Pago de prueba",
        }

    @pytest.fixture
    def invalid_address_request(self):
        """Fixture con dirección inválida"""
        return {
            "recipient_address": "0xinvalid",
            "amount": 100.50,
            "stablecoin": "USDC",
        }

    @pytest.fixture
    def invalid_amount_request(self):
        """Fixture con monto inválido"""
        return {
            "recipient_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f1bEb",
            "amount": 0.001,  # Muy pequeño
            "stablecoin": "USDC",
        }

    @pytest.fixture
    def invalid_stablecoin_request(self):
        """Fixture con stablecoin inválido"""
        return {
            "recipient_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f1bEb",
            "amount": 100.50,
            "stablecoin": "INVALID",
        }

    # ==================== TESTS POST /payments/create ====================

    def test_create_payment_success(self, client, valid_payment_request):
        """Test crear pago exitosamente"""
        with patch("routes.payments.payment_service_instance") as mock_service:
            mock_service.create_payment = AsyncMock(
                return_value={
                    "payment_id": "test-id-123",
                    "tx_hash": "0xabc123",
                    "recipient": valid_payment_request["recipient_address"],
                    "amount": valid_payment_request["amount"],
                    "stablecoin": valid_payment_request["stablecoin"],
                    "status": "pending",
                    "created_at": "2024-01-01T12:00:00Z",
                }
            )

            response = client.post(
                "/payments/create",
                json=valid_payment_request,
            )

            assert response.status_code == 201
            data = response.json()
            assert data["success"] is True
            assert "data" in data
            assert data["data"]["payment_id"] == "test-id-123"

    def test_create_payment_invalid_address(self, client, invalid_address_request):
        """Test crear pago con dirección inválida"""
        response = client.post(
            "/payments/create",
            json=invalid_address_request,
        )

        assert response.status_code == 422  # Validación Pydantic
        data = response.json()
        assert "detail" in data

    def test_create_payment_invalid_amount(self, client, invalid_amount_request):
        """Test crear pago con monto inválido"""
        response = client.post(
            "/payments/create",
            json=invalid_amount_request,
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_create_payment_invalid_stablecoin(
        self, client, invalid_stablecoin_request
    ):
        """Test crear pago con stablecoin inválido"""
        response = client.post(
            "/payments/create",
            json=invalid_stablecoin_request,
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_create_payment_service_error(self, client, valid_payment_request):
        """Test crear pago con error en servicio"""
        with patch("routes.payments.payment_service_instance") as mock_service:
            mock_service.create_payment = AsyncMock(
                side_effect=ValueError("Error de validación")
            )

            response = client.post(
                "/payments/create",
                json=valid_payment_request,
            )

            assert response.status_code == 400
            data = response.json()
            assert data["success"] is False

    def test_create_payment_service_not_available(self, client, valid_payment_request):
        """Test crear pago cuando servicio no está disponible"""
        with patch("routes.payments.payment_service_instance", None):
            response = client.post(
                "/payments/create",
                json=valid_payment_request,
            )

            assert response.status_code == 503
            data = response.json()
            assert "Payment service not available" in data["detail"]

    # ==================== TESTS GET /payments/status/{tx_hash} ====================

    def test_get_payment_status_success(self, client):
        """Test obtener estado de pago exitosamente"""
        tx_hash = "0x" + "a" * 64

        with patch("routes.payments.payment_service_instance") as mock_service:
            mock_service.get_payment_status = AsyncMock(
                return_value={
                    "payment_id": "test-id",
                    "tx_hash": tx_hash,
                    "status": "pending",
                    "confirmations": 0,
                    "block_number": None,
                }
            )

            response = client.get(f"/payments/status/{tx_hash}")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["tx_hash"] == tx_hash

    def test_get_payment_status_invalid_hash(self, client):
        """Test obtener estado con hash inválido"""
        invalid_hash = "0xinvalid"

        response = client.get(f"/payments/status/{invalid_hash}")

        assert response.status_code == 400
        data = response.json()
        assert "Invalid transaction hash" in data["detail"]

    def test_get_payment_status_not_found(self, client):
        """Test obtener estado de pago no encontrado"""
        tx_hash = "0x" + "a" * 64

        with patch("routes.payments.payment_service_instance") as mock_service:
            mock_service.get_payment_status = AsyncMock(
                side_effect=ValueError("No payment found")
            )

            response = client.get(f"/payments/status/{tx_hash}")

            assert response.status_code == 404
            data = response.json()
            assert data["success"] is False

    # ==================== TESTS GET /payments/by-id/{payment_id} ====================

    def test_get_payment_by_id_success(self, client):
        """Test obtener pago por ID"""
        payment_id = "123e4567-e89b-12d3-a456-426614174000"

        with patch("routes.payments.payment_service_instance") as mock_service:
            mock_service.get_payment_status = AsyncMock(
                return_value={
                    "payment_id": payment_id,
                    "tx_hash": "0xabc123",
                    "status": "pending",
                }
            )

            response = client.get(f"/payments/by-id/{payment_id}")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["payment_id"] == payment_id

    def test_get_payment_by_id_not_found(self, client):
        """Test obtener pago por ID no encontrado"""
        payment_id = "invalid-id"

        with patch("routes.payments.payment_service_instance") as mock_service:
            mock_service.get_payment_status = AsyncMock(
                side_effect=ValueError("Payment not found")
            )

            response = client.get(f"/payments/by-id/{payment_id}")

            assert response.status_code == 404

    # ==================== TESTS GET /payments/all ====================

    def test_get_all_payments_success(self, client):
        """Test obtener todos los pagos"""
        with patch("routes.payments.payment_service_instance") as mock_service:
            mock_service.get_all_payments = MagicMock(
                return_value=[
                    {
                        "payment_id": "id1",
                        "status": "pending",
                    },
                    {
                        "payment_id": "id2",
                        "status": "completed",
                    },
                ]
            )

            response = client.get("/payments/all")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["total"] == 2
            assert len(data["data"]["payments"]) == 2

    def test_get_all_payments_empty(self, client):
        """Test obtener pagos cuando lista está vacía"""
        with patch("routes.payments.payment_service_instance") as mock_service:
            mock_service.get_all_payments = MagicMock(return_value=[])

            response = client.get("/payments/all")

            assert response.status_code == 200
            data = response.json()
            assert data["data"]["total"] == 0
            assert data["data"]["payments"] == []

    # ==================== TESTS GET /payments/by-status/{status} ====================

    def test_get_payments_by_status_pending(self, client):
        """Test obtener pagos en estado pending"""
        with patch("routes.payments.payment_service_instance") as mock_service:
            mock_service.get_payments_by_status = MagicMock(
                return_value=[
                    {
                        "payment_id": "id1",
                        "status": "pending",
                    }
                ]
            )

            response = client.get("/payments/by-status/pending")

            assert response.status_code == 200
            data = response.json()
            assert data["data"]["status"] == "pending"
            assert data["data"]["total"] == 1

    def test_get_payments_by_status_completed(self, client):
        """Test obtener pagos completados"""
        with patch("routes.payments.payment_service_instance") as mock_service:
            mock_service.get_payments_by_status = MagicMock(return_value=[])

            response = client.get("/payments/by-status/completed")

            assert response.status_code == 200
            data = response.json()
            assert data["data"]["status"] == "completed"

    def test_get_payments_by_status_invalid(self, client):
        """Test obtener pagos con estado inválido"""
        response = client.get("/payments/by-status/invalid_status")

        assert response.status_code == 400
        data = response.json()
        assert "Invalid status" in data["detail"]

    def test_get_payments_by_status_success_alias(self, client):
        """Test que 'success' es alias de 'completed'"""
        with patch("routes.payments.payment_service_instance") as mock_service:
            mock_service.get_payments_by_status = MagicMock(return_value=[])

            response = client.get("/payments/by-status/success")

            assert response.status_code == 200


class TestPaymentValidation:
    """Tests para validaciones de pagos"""

    def test_create_payment_request_model(self):
        """Test modelo CreatePaymentRequest"""
        valid_data = {
            "recipient_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f1bEb",
            "amount": 100.50,
            "stablecoin": "USDC",
            "description": "Test",
        }

        request = CreatePaymentRequest(**valid_data)
        assert request.recipient_address == valid_data["recipient_address"]
        assert request.amount == valid_data["amount"]
        assert request.stablecoin == "USDC"

    def test_create_payment_request_invalid_address(self):
        """Test modelo con dirección inválida"""
        invalid_data = {
            "recipient_address": "invalid",
            "amount": 100.50,
            "stablecoin": "USDC",
        }

        with pytest.raises(ValueError):
            CreatePaymentRequest(**invalid_data)

    def test_create_payment_request_amount_validation(self):
        """Test validación de monto"""
        # Monto muy pequeño
        small_amount_data = {
            "recipient_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f1bEb",
            "amount": 0.001,
            "stablecoin": "USDC",
        }

        with pytest.raises(ValueError):
            CreatePaymentRequest(**small_amount_data)

        # Monto muy grande
        large_amount_data = {
            "recipient_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f1bEb",
            "amount": 2_000_000,
            "stablecoin": "USDC",
        }

        with pytest.raises(ValueError):
            CreatePaymentRequest(**large_amount_data)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
